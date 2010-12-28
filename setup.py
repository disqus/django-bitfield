#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
    from setuptools.command.test import test
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages
    from setuptools.command.test import test


class mytest(test):
    def run(self, *args, **kwargs):
        from runtests import runtests
        runtests()

setup(
    name='django-bitfield',
    version='1.0.1',
    author='DISQUS',
    author_email='opensource@disqus.com',
    url='http://github.com/disqus/django-bitfield',
    description = 'BitField in Django',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[],
    test_suite = 'bitfield.tests',
    include_package_data=True,
    cmdclass={"test": mytest},
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)