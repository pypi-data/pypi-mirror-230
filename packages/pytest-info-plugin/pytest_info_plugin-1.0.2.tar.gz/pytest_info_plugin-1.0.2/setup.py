from setuptools import setup
from setuptools import find_packages


VERSION = '1.0.2'

setup(
    name='pytest_info_plugin',  # package name
    version=VERSION,  # package version
    description='Get executed interface information in pytest interface automation framework',  # package description
    zip_safe=False,
    install_requires=[
        "pytest",
    ],
    entry_points={
        'pytest11': [
            'pytest_info_plugin = pytest_info_plugin',
        ],
    },

)