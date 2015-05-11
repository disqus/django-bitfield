from __future__ import absolute_import

import os.path
import sys

from django.conf import settings


sys.path.insert(0, os.path.dirname(__file__))


def pytest_configure(config):
    if not settings.configured:
        test_db = os.environ.get('DB', 'postgres')

        DATABASES = {
            'default': {
                'NAME': 'bitfield',
            }
        }

        if test_db == 'postgres':
            DATABASES['default'].update({
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'USER': 'postgres',
            })
        elif test_db == 'sqlite':
            DATABASES['default'].update({
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            })

        settings.configure(
            DATABASES=DATABASES,
            INSTALLED_APPS=[
                'django.contrib.contenttypes',
                'bitfield',
                'bitfield.tests',
            ],
            ROOT_URLCONF='',
            DEBUG=False,
        )
