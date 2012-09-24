# -*- coding:utf-8 -*-

from django.conf import settings

# Here you can override any settings from coop default settings files
# See :
# - coop/default_project_settings.py
# - coop/db_settings.py

SITE_AUTHOR = 'Organisme'
SITE_TITLE = 'Demo Django-coop'
DEFAULT_URI_DOMAIN = '{{ domain }}'

D2RQ_PORT = 8080
D2RQ_ROOT = 'http://{{ domain }}:8080/' + settings.PROJECT_NAME + '/'


DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Administrateur', 'web@quinode.fr'),
)

MANAGERS = ADMINS
SEND_BROKEN_LINK_EMAILS = True
INTERNAL_IPS = ('127.0.0.1', '92.243.30.98')

SUBHUB_MAINTENANCE_AUTO = False    # set this value to True to automatically syncronize with agregator
PES_HOST = 'pes.domain.com'
THESAURUS_HOST = 'thess.domain.com'

INSTALLED_APPS = settings.INSTALLED_APPS + [
    # select your coop components
    'coop.tag',
    'coop.agenda',
    'coop.article',
    'coop.mailing',
    'coop.exchange',
    #'coop.webid',
    'coop_local',
     # coop optional modules
    'coop_geo',  # est obligatoirement APRES coop_local

]

# TODO: to be discuss this settings could be in default_project_setings.py
# file. To be check I knew more on how to configure sympa
SYMPA_SOAP = {
    'WSDL': 'http://sympa.{{ domain }}/sympa/wsdl',
    'APPNAME': 'djangoapp',
    'PASSWORD': 'test',
    'OWNER': 'USER_EMAIL=userProxy@my.server',
    'PARAMETER_SEPARATOR': '__SEP__',      # used for template
}
