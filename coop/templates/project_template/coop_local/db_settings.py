# -*- coding:utf-8 -*-

from coop_local.settings import PROJECT_NAME

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': PROJECT_NAME,                      # Or path to database file if using sqlite3.
        'USER': 'admin',                      # Not used with sqlite3.
        'PASSWORD': '123456',                  # Not used with sqlite3.
   },
    'geofla_db': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'anotherdb',                      # Or path to database file if using sqlite3.
        'USER': 'admin',                      # Not used with sqlite3.
        'PASSWORD': '123456',                  # Not used with sqlite3.
    },
}

