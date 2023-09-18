from setuptools import setup
from setuptools import find_packages

VERSION = '0.1.0'

setup(
    name='idb-answer',
    version=VERSION,
    description='idb desc',
    packages=find_packages(),
    zip_safe=False,
    author='answer.huang',
    author_email='answer.huang@nio.com',
    keywords='idb-answer'
)