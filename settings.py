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
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'dbname',                      # Or path to database file if using sqlite3.
        'USER': 'postgres',                      # Not used with sqlite3.
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
    #os.path.abspath(PROJECT_PATH+'/djaloha/static/'),
    #os.path.abspath(PROJECT_PATH+'/coop_cms/static/'),
    # os.path.abspath(PROJECT_PATH+'/coop_geo/static/'),
    # os.path.abspath(PROJECT_PATH+'/coop/static/'),
    # os.path.abspath(PROJECT_PATH+'/rss_sync/static/'),
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

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'coop.utils.cors.CORSMiddleware'
]

LOCALE_PATHS = (
    os.path.abspath(PROJECT_PATH+'/coop/exchange/locale'),
    os.path.abspath(PROJECT_PATH+'/coop/initiative/locale'),
    os.path.abspath(PROJECT_PATH+'/coop/link/locale'),
    os.path.abspath(PROJECT_PATH+'/coop/membre/locale'),
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.abspath(PROJECT_PATH+'/templates/'),
    'coop_bar/templates',
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
    # needed to build links to the D2RQ pages
    "coop.context_processors.d2rq_settings",
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

INSTALLED_APPS = [
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
    'django.contrib.gis',
    'django.contrib.comments',

    #3rd parties
    'south',
    'django_extensions',
    'extended_choices',
    'smart_selects',
    'livesettings',
    'sorl.thumbnail',
    'floppyforms',
    #'haystack',
    'html_field',
    'oembed',
    'chosen',

    #apps
    'coop',
    'coop_local',
    'coop_tag',
    'djaloha',
    'coop_cms',
    'skosxl',
    'rss_sync',
    'coop_geo',
    
    'coop_agenda',
    'coop_bar',
    'taggit',
    'taggit_templatetags',
    #'taggit_autocomplete_modified',
    'taggit_autosuggest',
    
]

THUMBNAIL_FORMAT = 'PNG'

# Sequence for each optional app as a dict containing info about the app.
OPTIONAL_APPS = (
    {"import": 'geodjangofla', "apps": ('geodjangofla',)},
)

# Set up each optional app if available.
for app in OPTIONAL_APPS:
    if app.get("condition", True):
        try:
            __import__(app["import"])
        except ImportError:
            pass
        else:
            INSTALLED_APPS += app.get("apps", ())
            MIDDLEWARE_CLASSES += app.get("middleware", ())


DJALOHA_LINK_MODELS = ('coop_local.Article',)

DJALOHA_LINK_MODELS = ('coop_local.Article','coop_local.Initiative')
COOP_CMS_ARTICLE_CLASS = 'coop_local.models.Article'
COOP_CMS_ARTICLE_FORM = 'coop_local.forms.ArticleForm'
COOP_CMS_ARTICLE_TEMPLATES = 'coop_local.get_article_templates'
COOP_CMS_ARTICLE_LOGO_SIZE = '600'



D2RQ_ROOT = 'http://demo.django.coop:2020/'

HAYSTACK_SITECONF = 'coop_local.search_sites'
HAYSTACK_SEARCH_ENGINE = 'simple'
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

ADMIN_TOOLS_MENU = 'coop_local.menu.CustomMenu'
ADMIN_TOOLS_INDEX_DASHBOARD = 'coop_local.dashboard.CustomIndexDashboard'
ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'coop_local.dashboard.CustomAppIndexDashboard'
ADMIN_TOOLS_THEMING_CSS = 'css/coop_theming.css'

LIVESETTINGS_OPTIONS = \
{
    1: {
    'DB': True,
       'SETTINGS': {
            u'coop_cms': {u'CONTENT_APPS': u'["coop_cms"]'}
        }
    }
}


AUTH_PROFILE_MODULE = 'coop_local.membre'

SITE_AUTHOR = 'CREDIS'
SITE_TITLE = 'CREDIS : Collectif Régional des Initiatives Solidaires en Auvergne'

# projection used in database
COOP_GEO_EPSG_PROJECTION = 4326 # WGS84

COOP_GEO_BOUNDING_BOX = []
COOP_GEO_REGION = LANGUAGE_CODE[:2]

TAGGIT_TAG_MODEL           = ('skosxl','Label')
TAGGIT_TAGGED_ITEM_MODEL   = ('skosxl','LabelledItem')
TAGGIT_AUTOCOMPLETE_TAG_MODEL = 'skosxl.Label'

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
