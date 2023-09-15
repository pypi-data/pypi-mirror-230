import datetime
import pytz
import logging
import uuid
import re
import traceback

from google.cloud import firestore

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

class FirestoreAdministrator():

    def __init__(self):
        self.db = firestore.Client()

    def increment_field(self, collection_id, document_id, increment_dict):
        try:
            ref = self.db.collection(str(collection_id)).document(str(document_id))
            for key, _ in increment_dict.items():
                new_key = re.sub('[\W_]+', '',key)
                if new_key != key:
                    LOG.info(f"renaming {key} to {new_key}")
            firestore_increment_dict = {
                re.sub('[\W_]+', '',key):
                    firestore.Increment(value)
                for key, value in increment_dict.items()}
            LOG.info(f"incrementing {increment_dict} in {collection_id} {document_id}")
            ref.update(firestore_increment_dict)
        except Exception as exc:
            error_text = (
                "Exception while incrementing firestore field.\n"
                f"collection: {collection_id}\n"
                f"document: {document_id}\n"
                f"increment_dict: {increment_dict}\n"
                f"Stacktrace:\n{traceback.format_exc()}\n"
                f"Exception: {exc}")
            LOG.error(error_text)

    def add_document_to_collection(self, collection_id, document_id, data):
        try:
            doc_ref = self.db.collection(str(collection_id)).document(str(document_id))
            data['firestore_creation_timestamp'] = firestore.SERVER_TIMESTAMP
            doc_ref.set(data, merge=True)
            now = datetime.datetime.now(pytz.utc)
            datetime_string = now.strftime("%Y-%m-%d--%H-%M-%Z")
            data['firestore_creation_timestamp'] = datetime_string
            LOG.info(f"Added {document_id} document to {collection_id} firestore collection.")
        except Exception as exc:
            error_text = (
                "Exception while while writing to firestore.\n"
                f"collection: {collection_id}\n"
                f"document: {document_id}\n"
                f"data: {data}\n"
                f"Stacktrace:\n{traceback.format_exc()}\n"
                f"Exception: {exc}")
            LOG.error(error_text)

    def update_document_in_collection(self, collection_id, document_id, data):
        try:
            current_datetime = datetime.datetime.now(pytz.utc)
            current_datestamp = current_datetime.strftime('%Y-%m-%d_%H:%M:%S_%Z%z')
            uuid4 = str(uuid.uuid4())
            doc_dict = self.get_firebase_doc_dict(collection_id, document_id)
            if doc_dict != None:
                new_collection_id = collection_id + "_archive"
                new_document_id = document_id + "_" + current_datestamp + "_" + str(uuid4)
                self.add_document_to_collection(
                    new_collection_id,
                    new_document_id,
                    doc_dict)
            self.add_document_to_collection(
                collection_id, document_id, data)
        except Exception as exc:
            LOG.error(f"Exception while writing to firestore.")
            LOG.error(f"collection: {collection_id}")
            LOG.error(f"document: {document_id}")
            LOG.error(f"data: {data}")
            LOG.error(f"Stacktrace: {traceback.print_stack()}")
            LOG.error(f"Exception: {exc}")

    def query_firebase(self, collection_id, document_id, query):
        doc_dict = self.get_firebase_doc_dict(collection_id, document_id)
        if(doc_dict != None):
            return doc_dict[query]
        else:
            return None

    # def get_firebase_docs(self, collection_id):
    #     collection_ref = self.db.collection(str(collection_id))
    #     docs_ref = collection_ref.stream()

    #     for doc in docs_ref:
    #         print(f'{doc.id} => {doc.to_dict()}')

    def get_firebase_doc_dict(self, collection_id, document_id):
        collection_ref = self.db.collection(str(collection_id))
        doc_ref = collection_ref.document(str(document_id))
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            return None

    def list_collections(self):
        return [col.id for col in self.db.collections()]
