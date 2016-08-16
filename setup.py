#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-bitfield',
    version='1.9.0',
    author='DISQUS',
    author_email='opensource@disqus.com',
    url='https://github.com/disqus/django-bitfield',
    description='BitField in Django',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'Django>=1.10',
        'six',
    ],
    extras_require={
        'tests': [
            'flake8',
            'mysqlclient',
            'psycopg2>=2.3',
            'pytest-django',
        ],
    },
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
    ],
)
