#!/usr/bin/env python

import ast
import os.path
from setuptools import setup, find_packages

class GetVersion(ast.NodeVisitor):
    def __init__(self, path):
        with open(path) as f:
            self.visit(ast.parse(f.read(), path))

    def visit_Assign(self, node):
        if any(target.id == 'VERSION' for target in node.targets):
            assert not hasattr(self, 'VERSION')
            self.VERSION = node.value.s

setup(
    name='django-bitfield',
    version=GetVersion(os.path.join(os.path.dirname(__file__), 'bitfield', '__init__.py')).VERSION,
    author='Disqus',
    author_email='opensource@disqus.com',
    url='https://github.com/disqus/django-bitfield',
    description='BitField in Django',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'Django>=1.4.22',
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
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
)
