# -*- coding:utf-8 -*-

SITE_AUTHOR = 'Organisme'
SITE_TITLE = 'Demo Django-coop'
DEFAULT_URI_DOMAIN = 'mydomain.com'

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Administrateur', 'web@quinode.fr'),
)

MANAGERS = ADMINS
SEND_BROKEN_LINK_EMAILS = True
INTERNAL_IPS = ('127.0.0.1', '92.243.30.98')

from django.conf import settings

INSTALLED_APPS = settings.INSTALLED_APPS + [
    # select your coop components
    'coop.tag',
    'coop.agenda',
    'coop.article',
    'coop.mailing',
    'coop.exchange',
    'coop.org',
    'coop.person',
    'coop.ui',
    #'coop.webid',
    'coop_geo',
    'coop_local',
]