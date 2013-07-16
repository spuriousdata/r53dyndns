#!/usr/bin/env python
from setuptools import setup

setup(
    name='django-r53dyndns',
    version='0.1.0',
    description='A dynamic dns server using Amazon route53 and Django.',
    license='LICENSE',
    author="Mike O'Malley",
    author_email='spuriousdata@gmail.com',
    url='http://github.com/spuriousdata/django-r53dyndns',
    install_requires=[
        'Django >= 1.5',
        'boto',
    ],
    packages=[
        'r53dyndns',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License'
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
