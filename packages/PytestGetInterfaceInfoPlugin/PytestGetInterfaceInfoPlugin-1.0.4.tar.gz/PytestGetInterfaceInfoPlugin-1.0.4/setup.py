from setuptools import setup
from setuptools import find_packages


VERSION = '1.0.4'

setup(
    name='PytestGetInterfaceInfoPlugin',  # package name
    version=VERSION,  # package version
    description='Get executed interface information in pytest interface automation framework',  # package description
    zip_safe=False,
    install_requires=[
        "pytest",
    ],  
    entry_points={
        'pytest11': [
            'PytestGetInterfaceInfoPlugin = PytestGetInterfaceInfoPlugin',
        ],
    },

)