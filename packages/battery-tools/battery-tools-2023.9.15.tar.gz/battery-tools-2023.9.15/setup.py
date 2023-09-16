__version__ = '2023.09.15'
__author__ = 'PABLO PILA'
__author_email__ = "pablogonzalezpila@gmail.com"

''' 
NOTES:
TASK:
WARNINGS:
'''

from setuptools import setup, find_packages

setup(
    name = "battery-tools",
    version = __version__,
    author = __author__,
    author_email = __author_email__,
    url = "https://github.com/PaulFilms/battery-tools.git",
    packages = find_packages(),
    license = "MIT",
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        ]
)