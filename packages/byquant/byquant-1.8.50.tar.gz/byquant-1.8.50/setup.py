# prefer setuptools over distutils
from setuptools import setup, find_packages

# use a consistent encoding
from codecs import open
from os import path
import json
import sys

is_python_2 = sys.version_info < (3, 0)

here = path.abspath(path.dirname(__file__))
root = path.dirname(here)

readme = path.join(here, 'README.md')
package = {
  "name": "byquant",
  "version": "1.8.50",
  "description": "ByQuant.com is AI Quantitative Strategy Competition Training Community",
  "type": "module",
  "readme": "README.md",
  "package_json": "package.json",
  "author": {
    "name": "Uakeey",
    "email": "uakee@outlook.com",
    "url": "https://github.com/byquantcom/"
  },
  "license": "GPL",
  "bugs": {
    "url": "https://github.com/byquantcom/byquant/issues"
  },
  "homepage": "https://byquant.com",
  "keywords": [
    "quant",
    "strategy",
    "algorithmic",
    "algotrading"
  ]
}



# long description from README file
with open(readme, encoding='utf-8') as f:
    long_description = f.read()


project_urls = {
    'Homepage': 'https://byquant.com',
}

setup(
    name=package['name'],
    version=package['version'],

    description=package['description'],
    long_description=long_description,
    long_description_content_type='text/markdown',

    url=package['homepage'],

    author=package['author']['name'],
    author_email=package['author']['email'],

    license=package['license'],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Information Technology',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Office/Business :: Financial :: Investment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: JavaScript',
        'Programming Language :: PHP',
        'Operating System :: OS Independent',
        'Environment :: Console'
    ],
    keywords=package['keywords'],
    packages=find_packages(exclude=['byquant.async_support*'] if is_python_2 else []),
    install_requires=[
        'setuptools>=60.9.0',
        'certifi>=2018.1.18',
        'requests>=2.18.4',
        'cryptography>=2.6.1'
    ],
    project_urls=project_urls,
    zip_safe=True,
)