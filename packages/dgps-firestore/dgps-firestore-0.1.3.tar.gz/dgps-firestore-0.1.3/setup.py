import os
from setuptools import setup

with open("VERSION", "r") as version_file:
    version = version_file.read().strip()

# Get the subpackage to include from the environment variable
subpackage_to_include = os.environ.get('SUBPACKAGE_TO_INCLUDE', 'firestore')
subpackages_to_include = subpackage_to_include.split(',')

# Construct the distribution name dynamically
distribution_name = f"dgps-{subpackage_to_include}"

# Read the requirements from the respective requirements.txt
required_packages = []
package_list = ['dgps']
for _subpackage_to_include in subpackages_to_include:
    package_list.append(f'dgps.{_subpackage_to_include}')
    with open(os.path.join('dgps', _subpackage_to_include, 'requirements.txt')) as f:
        required_packages.append(f.read().splitlines())

setup(
    name=distribution_name,
    version=version,
    url="https://www.democracygps.org/team",
    author="Chris Krenn",
    author_email="crkrenn@gmail.com",
    description="Utility functions for DemocracyGPS",
    packages=package_list,  # Only include the dgps package and the specified subpackage
    install_requires=required_packages,
)
