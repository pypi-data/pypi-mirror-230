from setuptools import setup
from setuptools import find_packages


VERSION = '0.1.0'

setup(
    name='pytest-info-plugin',  # package name
    version=VERSION,  # package version
    description='Get executed interface information in pytest interface automation framework',  # package description
    package_data={
        "": ["conftest.py"],
    },
    zip_safe=False,
    install_requires=[
        "ast",
        "datetime",
        "inspect",
        "re",
        "time",
        "pytest",
        "importlib",
    ],

)