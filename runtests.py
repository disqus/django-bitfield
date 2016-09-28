#!/usr/bin/env python
import sys
from optparse import OptionParser

from django.conf import settings

if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'bitfield_test',
                'USER': 'postgres',
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


from django_nose import NoseTestSuiteRunner


def runtests(*test_args, **kwargs):
    if 'south' in settings.INSTALLED_APPS:
        from south.management.commands import patch_for_test_db_setup
        patch_for_test_db_setup()

    if not test_args:
        test_args = ['bitfield']

    try:
        from django.test.runner import DiscoverRunner
        test_runner = DiscoverRunner(**kwargs)
    except ImportError:
        test_runner = NoseTestSuiteRunner(**kwargs)

    import django
    try:
        django.setup()
    except AttributeError:
        pass

    failures = test_runner.run_tests(test_args)
    sys.exit(failures)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--verbosity', dest='verbosity', action='store', default=1, type=int)
    parser.add_options(NoseTestSuiteRunner.options)
    (options, args) = parser.parse_args()

    runtests(*args, **options.__dict__)
