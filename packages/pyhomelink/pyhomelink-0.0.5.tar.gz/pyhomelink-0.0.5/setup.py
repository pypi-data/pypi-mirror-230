"""Setup skyq_hub package."""
from setuptools import setup, find_namespace_packages

from pyhomelink.version import __version__ as version

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pyhomelink',
    version=version,
    author='Roger Selwyn',
    author_email='roger.selwyn@nomail.com',
    description='Library for AICO HomeLINK',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/RogerSelwyn/python_homelink',
    license='MIT',
    packages=find_namespace_packages(exclude=['tests','manage']),
    install_requires=['aiohttp>=3.8.5'],
    keywords='AICO HomeLINK',
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.10'	
)
