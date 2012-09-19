# -*- coding:utf-8 -*-
# Django settings for {{ project_name }} project.

from django.core.exceptions import ImproperlyConfigured

DEBUG = False
TEMPLATE_DEBUG = DEBUG

SECRET_KEY = '{{ secret_key }}'

import os.path
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#PROJECT_NAME = PROJECT_PATH.split('/')[-1]
PROJECT_NAME = '{{ project_name }}'  # which one is safer ?


# import all default app settings from django-coop app

try:
    from coop.default_project_settings import *
except ImportError, exp:
    raise ImproperlyConfigured("Unable to find default_project_settings.py file from django-coop : ", exp)

# override settings when needed in local_settings.py

try:
    from local_settings import *
except ImportError, exp:
    pass

# debug settings : load dev tools (FireLogger & Django debug Toolbar) or setup Sentry Logging
try:
    DEBUG_SETTINGS = {  'apps': INSTALLED_APPS,
                        'middleware': MIDDLEWARE_CLASSES,
                        'logging': LOGGING
                        }
    from coop.debug_settings import *
except ImportError, exp:
    raise ImproperlyConfigured("Unable to find coop/debug_settings.py file in django-coop : ", exp)


# db_settings file for DATABASES, and CACHE backend settings

try:
    from db_settings import *
except ImportError, exp:
    raise ImproperlyConfigured("Unable to find db_settings.py file from coop_local project : ", exp)


# common db_settings file for DATABASE ROUTERS

try:
    from coop.db_settings import *
except ImportError, exp:
    raise ImproperlyConfigured("Unable to find coop/db_settings.py file in django-coop : ", exp)


