# -*- coding:utf-8 -*-
import os
from coop_local.settings import PROJECT_PATH, PROJECT_NAME

TIME_ZONE = 'Europe/Paris'
LANGUAGE_CODE = 'fr-FR'

from multisite import SiteID
SITE_ID = SiteID(default=1)
COOP_USE_SITES = False


USE_I18N = True
USE_L10N = True

DEFAULT_CONTENT_TYPE = 'text/html'
DEFAULT_CHARSET = 'utf-8'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'

USE_TZ = False

# Upload directory
MEDIA_ROOT = os.path.abspath(PROJECT_PATH + '/media/')
MEDIA_URL = '/media/'

# Static files
STATIC_ROOT = os.path.abspath(PROJECT_PATH + '/static_collected/')
STATIC_URL = '/static/'

# compat fix ?
ADMIN_MEDIA_PREFIX = STATIC_URL + "admin/"


import admin_tools
ADMIN_TOOLS_PATH = os.path.dirname(os.path.abspath(admin_tools.__file__))


STATICFILES_DIRS = [
    os.path.abspath(ADMIN_TOOLS_PATH + '/media/'),
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
]


TEMPLATE_DIRS = [
    os.path.abspath(PROJECT_PATH + '/coop_local/templates/')
]

TEMPLATE_LOADERS = [
    'multisite.template_loader.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
    'apptemplates.Loader',

]

MIDDLEWARE_CLASSES = [
    #'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'multisite.middleware.DynamicSiteMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'django_webid.auth.middleware.WEBIDAuthMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'coop.utils.middleware.CORSMiddleware',
    'pagination.middleware.PaginationMiddleware',
]

TEMPLATE_CONTEXT_PROCESSORS = [
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'coop.context_processors.current_site',
    'preferences.context_processors.preferences_cp',
]

ROOT_URLCONF = 'coop_local.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'coop_local.wsgi.application'

CACHE_MULTISITE_ALIAS = 'multisite'

# Cache middelware must be enabled above
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'memcached': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        #'LOCATION': '127.0.0.1:11211',
        'LOCATION': 'unix:/tmp/memcached.sock',
    },
    'multisite': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 60 * 60 * 24,  # 24 hours
    }
}

CACHE_MIDDLEWARE_ALIAS = 'memcached'
CACHE_MIDDLEWARE_SECONDS = 60 * 60
CACHE_MIDDLEWARE_KEY_PREFIX = PROJECT_NAME


# The view function or class-based view that django-multisite will
# use when it cannot match the hostname with a Site. This can be
# the name of the function or the function itself.
# Default: None
MULTISITE_FALLBACK = 'django.views.generic.base.RedirectView'

INSTALLED_APPS = [

    # admin tools
    'admintools_bootstrap',
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',

    # django contribs
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    #'django.contrib.admindocs', # ramène sa traduction de Tags "Étiquettes"...
    'django.contrib.gis',
    'django.contrib.comments',
    # 'djgeojson',

        # doit etre là sinon retour du bug #1796
    'django.contrib.sites',


    # other 3rd parties
    'south',
    'django_extensions',
    'extended_choices',
    'floppyforms',
    # 'haystack',
    # 'haystack_fr',
    #'oembed',
    'chosen',
    'sorl.thumbnail',
    'tinymce',
    'autoslug',
    'slugify',
    'forms_builder.forms',
    'preferences',
    'apptemplates',
    'scanredirect',
    'multisite',


    # WebID
    #'django_webid.provider',
    #'django_webid.auth',

    # coop apps
    'coop_tag',

    # 'feincms',  # for their MPTT tree editor, not synced
    'coop',  # override feincms tree editor template
    'coop.link',
    'coop.prefs',
    'coop.org',
    'coop.person',
    'coop.ui',
    'coop.rdf',
    # 'coop_geo',

    # PuSH
    'django_rq',
    'subhub',
    'django_push.subscriber',
    'uriredirect',

    # coop_cms
    'djaloha',
    'coop_cms',
    'coop_cms.apps.rss_sync',
    'colorbox',
    'coop_bar',
    'pagination',



]

MEDIA_TREE_ICON_DIRS = (
    'teambox/24x32px',  # the new folder under your static root | valid choices are 16px, 24x32px, and 48px
    'media_tree/img/icons/mimetypes',  # default icon folder
)

MEDIA_TREE_MEDIA_BACKENDS = (
    'media_tree.contrib.media_backends.easy_thumbnails.EasyThumbnailsBackend',
)

COOP_BAR_MODULES = [
    'coop.coop_bar_cfg',
    ]

AUTOSLUG_SLUGIFY_FUNCTION = 'slugify.slugify'

TAGGER_TAG_MODEL = 'coop_local.models.Tag'
TAGGER_TAGGEDITEM_MODEL = 'coop_local.models.TaggedItem'
TAGGER_FKEY_NAME = 'coop_local.Tag'

THUMBNAIL_FORMAT = 'PNG'
ADMIN_THUMBS_SIZE = '60x60'

TINYMCE_DEFAULT_CONFIG = {
    'theme': "advanced",
    'relative_urls': False,
    'width': '617px', 'height': '220px',
    'theme_advanced_toolbar_location': 'top',
    'theme_advanced_buttons1': 'bold,italic,|,justifyleft,justifycenter,justifyright,|,bullist,numlist,|,link,unlink,|,code',
    'theme_advanced_buttons2': '', 'theme_advanced_buttons3': ''
    }

COOP_NEWLETTER_ITEM_CLASSES = ['article']

COOP_CMS_ARTICLE_CLASS = 'coop_local.models.Article'
COOP_CMS_ARTICLE_FORM = 'coop.forms.ArticleForm'
COOP_CMS_ARTICLE_LOGO_SIZE = '600'


COOP_CMS_NAVTREE_CLASS = 'coop_local.NavTree'

# You need to declare the app here to be able to select models from navigable types in coop-cms
COOP_CMS_CONTENT_APPS = ('coop_local', 'coop_tag', 'coop_geo', 'coop_cms', 'forms')

DJALOHA_LINK_MODELS = (
        'coop_local.Article',
        'coop_cms.ArticleCategory',
        'coop_local.Organization',
        'coop_local.OrganizationCategory',
        'coop_local.Event',
        )



# COOP_CMS_ARTICLE_TEMPLATES = 'coop_local.get_article_templates' # marche plus ?

COOP_CMS_ARTICLE_TEMPLATES = [
    ('coop_cms/article.html', 'Standard'),
    ('coop_cms/article_nologo.html', 'Sans logo'),
]


SKIP_DJALOHA_JQUERY = True

FORMS_BUILDER_USE_SITES = False


ADMIN_TOOLS_MENU = 'coop.ui.menu.CustomMenu'
ADMIN_TOOLS_INDEX_DASHBOARD = 'coop.ui.dashboard.CustomIndexDashboard'
ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'coop.ui.dashboard.CustomAppIndexDashboard'
ADMIN_TOOLS_THEMING_CSS = 'css/coop_bootstrap_theming.css'


AUTHENTICATION_BACKENDS = [
    #'django_webid.auth.backends.WEBIDAuthBackend',
    'coop_cms.perms_backends.ArticlePermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_PROFILE_MODULE = 'coop_local.Person'

# projection used in database
COOP_GEO_EPSG_PROJECTION = 4326  # WGS84

COOP_GEO_BOUNDING_BOX = []
COOP_GEO_REGION = LANGUAGE_CODE[:2]


MEDIA_TREE_LIST_DISPLAY = ('browse_controls', 'size_formatted', 'extension',
    'get_descendant_count_display', 'modified', 'metadata_check', 'node_tools')
#
# WebID Options
#

WEBIDAUTH_USE_COOKIE = True

# The following lines set the local user creation callback.
# All the info from the remote profile is accessible from
# the request.webidinfo object (see documentation).


def createusercb(req):
    from coop.webid.utils import build_coop_user
    return build_coop_user(req)

WEBIDAUTH_CREATE_USER_CALLBACK = createusercb

WEBIDPROVIDER_SKIP_PROFILE_INIT = True

# Uncomment the following lines if you want to specify
# a custom callback for the assigment of the WebIDUris.
# If this callback is not specified, provider will look for
# a webidprovider-webid_uri urlpattern and will try to
# reverse it passing the webiduser instance.

#def webidcb(webiduser):
#    "avoids circular import"
#    from coop.webid.utils import custom_webid_uri
#    return custom_webid_uri(webiduser)
#WEBIDPROVIDER_WEBIDURI_CALLBACK = webidcb


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simplest': {
            'format': '%(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },

    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'console-dumb': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simplest'
        },

        # access denied problem on prod env.... to be check
        #  'file_subhub': {  # define and name a handler
        #     'level': 'DEBUG',
        #     'formatter': 'simple',
        #     'class': 'logging.handlers.WatchedFileHandler',  # set the logging class to log to a file
        #     'filename': os.path.abspath(PROJECT_PATH + '/logs/subhub.log')  # log file
        # },
        #  'file_rqworker': {  # define and name a handler
        #     'level': 'DEBUG',
        #     'formatter': 'simple',
        #     'class': 'logging.handlers.WatchedFileHandler',  # set the logging class to log to a file
        #     'filename': os.path.abspath(PROJECT_PATH + '/logs/rq.log')  # log file
        # },


    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        # 'subhub.maintenance': {
        #     'handlers': ['console'],
        #     'level': 'ERROR'
        # },
        # 'subhub.distribution.process': {
        #     'handlers': ['console'],
        #     'level': 'ERROR'

        # },
        'worker': {
            'handlers': ['console'],
            'level': 'DEBUG'

        },
        'coop': {
            'handlers': ['console-dumb'],
            'level': 'DEBUG',
        },
    },

}

# import default app settings from django-coop app

try:
    from coop.settings import *
except ImportError, exp:
    raise ImproperlyConfigured("Unable to find settings.py file from django-coop")
