# -*- coding: utf-8 -*-
from SOAPpy import WSDL, faultType
from django.conf import settings
from logging import getLogger
logger = getLogger('coop')

from django.core.exceptions import ImproperlyConfigured

try:
    sympa_soap = settings.SYMPA_SOAP
    try:
        _server = WSDL.Proxy(sympa_soap['WSDL'])
    except Exception, e:
        logger.warning(u"Cannot find find Sympa server - %s" % e)
except ImportError:
    raise ImproperlyConfigured("coop.mailing is installed but we need SYMPA_SOAP settings.")


def lists():
    try:
        return _server.authenticateRemoteAppAndRun(sympa_soap['APPNAME'],
                                                    sympa_soap['PASSWORD'],
                                                    'USER_EMAIL=' + sympa_soap['OWNER'],
                                                    'lists'
                                                    )
    except faultType, e:
        return e.faultstring


def info(name):
    try:
        return _server.authenticateRemoteAppAndRun(sympa_soap['APPNAME'],
                                                    sympa_soap['PASSWORD'],
                                                    'USER_EMAIL=' + sympa_soap['OWNER'],
                                                    'info',
                                                    (name,)
                                                    )
    except faultType, e:
        return e.faultstring


def exists(name):
    list_info = info(name)
    if list_info == 'Unknown list':
        return False
    else:
        return list_info


def create_list(name, subject, template, description, topics=u'topics'):
    try:
        return _server.authenticateRemoteAppAndRun(sympa_soap['APPNAME'],
                                                    sympa_soap['PASSWORD'],
                                                    'USER_EMAIL=' + sympa_soap['OWNER'],
                                                    'createList',
                                                    (name, subject, template, description, topics)
                                                    )
    except faultType, e:
        return e.faultstring


def close_list(name):
    try:
        return _server.authenticateRemoteAppAndRun(sympa_soap['APPNAME'],
                                                    sympa_soap['PASSWORD'],
                                                    'USER_EMAIL=' + sympa_soap['OWNER'],
                                                    'closeList',
                                                    (name,)
                                                    )
    except faultType, e:
        return e.faultstring
