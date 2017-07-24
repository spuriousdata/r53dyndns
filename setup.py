#!/usr/bin/env python
from setuptools import setup

setup(
    name='r53dyndns',
    version='0.3.0',
    description='A dynamic dns server using Amazon route53 and Flask.',
    license=open('LICENSE', 'r').read(),
    author="Mike O'Malley",
    author_email='spuriousdata at gmail dot com',
    url='http://github.com/spuriousdata/r53dyndns',
    install_requires=[
        'Flask >= 0.12',
        'boto3 >= 1.4.4',
    ],
    packages=[
        'r53dyndns',
    ],
    entry_points={
        'console_scripts': [
            'r5dadmin = r53dyndns.__main__:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License'
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
