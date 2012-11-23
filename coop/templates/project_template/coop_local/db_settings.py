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
        'NAME': PROJECT_NAME,                      # Or path to database file if using sqlite3.
        'USER': 'admin',                      # Not used with sqlite3.
        'PASSWORD': '123456',                  # Not used with sqlite3.
    },
}

# For redis
REDIS_PORT = 6379  # Please ask for a redis port to your administrator. Default value 6379, may already been used'

# # For django-rq, this mandatory to run rqworker command from manage.py
RQ_QUEUES = {
    'default': {
        'HOST': '127.0.0.1',
        'PORT': REDIS_PORT,
        'DB': 0,
    },
}


# Elastic search
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack_fr.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://localhost:9200/',
        'INDEX_NAME': settings.PROJECT_NAME,
        # 'INCLUDE_SPELLING': True,   # not yet handled by ES
    },
}

