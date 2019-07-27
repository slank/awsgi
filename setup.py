from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='aws-wsgi',

    version='0.1.1',

    description='WSGI adapter for AWS API Gateway/Lambda Proxy Integration',
    long_description=long_description,

    url='https://github.com/slank/awsgi',

    author='Matthew Wedgwood',
    author_email='github+awsgi@smacky.org',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='wsgi aws lambda api gateway',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
)
