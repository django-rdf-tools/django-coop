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
    # 'coop.mailing',   # the mailinglist management is HARDLY link to our sympa installation 
    # 'coop.project',  # Only if you need the Project module
    # 'coop.doc'  # Only if you need the Doc module
    'coop.exchange',
    #'coop.webid',
    'coop_local',
     # coop optional modules
    'coop_geo',  # est obligatoirement APRES coop_local
]

# TODO: to be discuss this settings could be in default_project_setings.py
# file. To be check I knew more on how to configure sympa
SYMPA_SOAP = {
    'WSDL': 'http://sympa.{{ root_domain }}/sympa/wsdl',
    'APPNAME': 'djangoapp',
    'PASSWORD': 'test',
    'OWNER': ADMINS[0][1],
    'PARAMETER_SEPARATOR': '__SEP__',      # used for template
}


# Keyword arguments for the MULTISITE_FALLBACK view.
# Default: {}
MULTISITE_FALLBACK_KWARGS = {}
