# -*- coding:utf-8 -*-

from django.conf import settings
import sys

# Here you can override any settings from coop default settings files
# See :
# - coop/default_project_settings.py
# - coop/db_settings.py

SITE_AUTHOR = 'Organisme'
SITE_TITLE = 'Demo Django-coop'
# DEFAULT_URI_DOMAIN = '{{ domain }}' useless use Site.objects.get_current().domain instead

# let this setting to False in production, except for urgent debugging
DEBUG = False

# Force DEBUG setting if we're developing locally or testing
if 'runserver' in sys.argv or 'test' in sys.argv:
    DEBUG = True

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Administrateur', 'web@quinode.fr'),
)

MANAGERS = ADMINS
SEND_BROKEN_LINK_EMAILS = True
INTERNAL_IPS = ('127.0.0.1', '92.243.30.98')

SUBHUB_MAINTENANCE_AUTO = False    # set this value to True to automatically syncronize with agregator
PES_HOST = 'http://pes.domain.com'
# THESAURUS_HOST = 'http://thess.domain.com'

# Need to be set to true, when domain stop moving,
# to keep history of renaming of uri
URI_FIXED = False  

INSTALLED_APPS = settings.INSTALLED_APPS + [
    # select your coop components
    'coop.tag',
    'coop.agenda',
    'coop.article',
    # 'coop.mailing',   # the mailinglist management, please configure the SYMPA_SOAP below 
    # 'coop.project',  # Only if you need the Project module
    # 'coop.doc'  # Only if you need the Doc module
    'coop.exchange',
    #'coop.webid',
    'coop_local',
     # coop optional modules
    'coop_geo',  # est obligatoirement APRES coop_local

    # Activate this to get Media_Tree and Ressources app
    # 'coop.doc',
    # 'mptt',
    # 'media_tree',
    # 'teambox_icons',
    # 'easy_thumbnails',
]

SYMPA_SOAP = {
    'WSDL': 'https://your-sympa-wsdl',
    'APPNAME': 'your-soap-app-name',
    'PASSWORD': 'your-soap_app-pw',
    'OWNER': '',  # email of the lists master
    # the following parameter are used for templates (see coop/mailing/sympa)
    'PARAMETER_SEPARATOR': '__SEP__',  # this separator is the one used in the templates s
    'SYMPA_TMPL_USER': '',  # set your sympa User username
    'SYMPA_TMPL_PASSWD': ''  # set your sympa User password
}


# Keyword arguments for the MULTISITE_FALLBACK view.
# Default: {}
MULTISITE_FALLBACK_KWARGS = {}
