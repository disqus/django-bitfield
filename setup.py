#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-bitfield',
    version='1.6.4',
    author='DISQUS',
    author_email='opensource@disqus.com',
    url='http://github.com/disqus/django-bitfield',
    description='BitField in Django',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'Django>=1.2',
    ],
    setup_requires=[
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
        'Topic :: Software Development'
    ],
)
