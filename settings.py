# -*- coding:utf-8 -*-
# Django settings for base project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG
import os.path
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

ADMINS = (
    ('Dom', 'contact@quinode.fr'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'base',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

TIME_ZONE = 'Europe/Paris'
LANGUAGE_CODE = 'fr-FR'
SITE_ID = 1
USE_I18N = True
USE_L10N = True

DEFAULT_CONTENT_TYPE = 'text/html'
DEFAULT_CHARSET='utf-8'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'


# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.abspath(PROJECT_PATH+'/media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.abspath(PROJECT_PATH+'/static_collected/')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

import admin_tools
ADMIN_TOOLS_PATH = os.path.dirname(os.path.abspath(admin_tools.__file__))

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.abspath(PROJECT_PATH+'/static/'),
    os.path.abspath(PROJECT_PATH+'/djaloha/static/'),
    os.path.abspath(PROJECT_PATH+'/coop_cms/static/'),
    os.path.abspath(PROJECT_PATH+'/coop/static/'),
    os.path.abspath(PROJECT_PATH+'/rss_sync/static/'),
    os.path.abspath(ADMIN_TOOLS_PATH+'/media/'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ibhc$tpzg&!8f3l-o@$c5y809j9)i=$v6dg6v@fzf^0ufmj8)q'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.abspath(PROJECT_PATH+'/templates/'),    
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "coop.context_processors.current_site",
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    'django.core.context_processors.request',
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

INSTALLED_APPS = (
    # Admin tools
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',

    # Contribs
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',

    #3rd parties
    'south',
    'django_extensions',
    'extended_choices',
    'smart_selects',
    'livesettings',
    'sorl.thumbnail',
    'floppyforms',
    
    #3rd parties integrated as regular apps
    'html_field',

    #apps
    'coop_local',
    'coop',
    'djaloha',
    'coop_cms',
    'skosxl',
    'rss_sync',
)

DJALOHA_LINK_MODELS = ('coop_cms.Article',)

#ADMIN_TOOLS_MENU = 'base.menu.CustomMenu'
#ADMIN_TOOLS_INDEX_DASHBOARD = 'base.dashboard.CustomIndexDashboard'
#ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'base.dashboard.CustomAppIndexDashboard'
#ADMIN_TOOLS_THEMING_CSS = 'css/coop_theming.css'

LIVESETTINGS_OPTIONS = \
{
    1: {
    'DB': True,
       'SETTINGS': {
            u'd2rq': {u'MAPPED_APPS': u'["coop_local", "skosxl"]'},
            u'coop_cms': {u'CONTENT_APPS': u'["coop_cms"]'}
        }
    }
}


AUTH_PROFILE_MODULE = 'coop_local.membre'

SITE_AUTHOR = 'CREDIS'
SITE_TITLE = 'CREDIS : Collectif Régional des Initiatives Solidaires en Auvergne'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

try:
    from local_settings import *
except ImportError, exp:
    pass
