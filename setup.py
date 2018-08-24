from setuptools import setup, find_packages

setup(
    name='genyrator',
    version='0.0.99',
    packages=find_packages(exclude=['test', 'bookshop', 'domain']),
    url='https://github.com/jumblesale/genyrator',
    license='',
    author='jumblesale',
    author_email='',
    description='',
    package_data={'': ['*.j2', ]},
    include_package_data=True,
    install_requires=[
        'attrs>=18.1',
        'inflection>=0.3',
    ],
)
