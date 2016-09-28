#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-bitfield',
    version='1.8.0',
    author='DISQUS',
    author_email='opensource@disqus.com',
    url='https://github.com/disqus/django-bitfield',
    description='BitField in Django',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'Django>=1.4',
        'six',
    ],
    setup_requires=[
        'nose>=1.0',
    ],
    tests_require=[
        'django-nose>=0.1.3',
        'psycopg2>=2.3',
    ],
    test_suite='runtests.runtests',
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
