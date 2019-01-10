import re
import sys

from setuptools import setup, find_packages


assert sys.version_info >= (3, 6, 0), "genyrator requires Python 3.6+"


with open('README.md', 'rt', encoding='utf8') as f:
    long_description = f.read()


with open('genyrator/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)


setup(
    name='genyrator',
    version=version,
    url='https://github.com/jumblesale/genyrator',
    project_urls={
        'Code': 'https://github.com/jumblesale/genyrator',
        'Issue tracker': 'https://github.com/jumblesale/genyrator/issues',
    },
    packages=find_packages(exclude=('test', 'test.*', 'bookshop', 'bookshop.*')),
    license='MIT',

    author='jumblesale',
    author_email='',

    description='A tool for generating a Flask web app from an abstract definition',
    long_description=long_description,
    long_description_content_type='text/markdown',

    package_data={'': ['*.j2', ]},
    include_package_data=True,

    python_requires=">=3.6",
    install_requires=[
        'attrs>=18.1',
        'inflection>=0.3',
    ],
)
