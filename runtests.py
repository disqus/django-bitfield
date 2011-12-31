#!/usr/bin/env python
import sys
from os.path import dirname, abspath
from optparse import OptionParser

from django.conf import settings

if not settings.configured:
    settings.configure(
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'bitfield_test',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'bitfield',
            'bitfield.tests',
        ],
        ROOT_URLCONF='',
        DEBUG=False,
    )

from django.test.simple import DjangoTestSuiteRunner

def runtests(*test_args):
    if not test_args:
        test_args = ['bitfield']
    parent = dirname(abspath(__file__))
    sys.path.insert(0, parent)
    interactive = '--no-input' not in sys.argv
    failures = DjangoTestSuiteRunner().run_tests(test_args, verbosity=1,
                                                 interactive=interactive)
    sys.exit(failures)

if __name__ == '__main__':
    parser = OptionParser()
    # parser.add_option('--verbosity', dest='verbosity', action='store', default=1, type=int)
    # parser.add_options(NoseTestSuiteRunner.options)
    (options, args) = parser.parse_args()

    runtests(*args, **options.__dict__)
