#!/usr/bin/env python
from optparse import OptionParser
from django.conf import settings
from django.core.management import call_command, setup_environ



def runtests(*test_args, **options):
    if not settings.configured:
        settings.configure(
            DATABASES = {
                'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory;'}
            },
            INSTALLED_APPS=[
                'bitfield',
                'bitfield.tests',
            ],
            ROOT_URLCONF='',
            DEBUG=False,
        )
    setup_environ(settings)
    # Fire off the tests
    call_command('test', 'bitfield', *test_args, **options)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--verbosity', dest='verbosity', action='store', default=1, type=int)
    (options, args) = parser.parse_args()

    runtests(*args, **options.__dict__)
