from setuptools import setup, find_packages

setup(
    name='genyrator',
    version='0.0.2',
    packages=find_packages(exclude=['tests']),
    url='https://github.com/jumblesale/genyrator',
    license='',
    author='jumblesale',
    author_email='',
    description='',
    install_requires=[
        'attrs>=18.1',
        'inflection>=0.3',
    ],
)
