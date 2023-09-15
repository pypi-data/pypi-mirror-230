from setuptools import setup
from setuptools import find_packages


VERSION = '0.1.0'

setup(
    name='InsCode',  # package name
    version=VERSION,  # package version
    description='Inscode SDK',  # package description
    packages=find_packages(),
    zip_safe=False,
)
