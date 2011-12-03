
import setuptools
import sys


requirements = ['httplib2']

if sys.version_info < (2, 6):
    requirements.append('simplejson')

setuptools.setup(
    name = "python-openstack-compute-v2",
    version = "1.0.0",
    description = "Client library for OpenStack Compute API v2",
    url = 'https://github.com/bcwaldon/python-openstack-compute-v2',
    author = 'Brian Waldon',
    author_email = 'bcwaldon@gmail.com',
    install_requires = requirements,
    packages = setuptools.find_packages(exclude=['tests', 'tests.*']),
)
