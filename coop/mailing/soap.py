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
        _server = None
        logger.warning(u"Cannot find find Sympa server - %s" % e)
except ImportError:
    raise ImproperlyConfigured("coop.mailing is installed but we need SYMPA_SOAP settings.")



def sympa_available():
    if _server: 
        return True
    return False


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
        if _server:
            return _server.authenticateRemoteAppAndRun(sympa_soap['APPNAME'],
                                                        sympa_soap['PASSWORD'],
                                                        'USER_EMAIL=' + sympa_soap['OWNER'],
                                                        'info',
                                                        (name,)
                                                        )
        else:
            return 'Unknown list'
    except faultType, e:
        logger.warning(e.faultstring)
        return 'Unknown list'


def exists(name):
    list_info = info(name)
    if list_info == 'Unknown list':
        return False
    else:
        return list_info


def create_list(name, subject, template, description, topics=u'topics'):
    try:
        if _server:
            return _server.authenticateRemoteAppAndRun(sympa_soap['APPNAME'],
                                                        sympa_soap['PASSWORD'],
                                                        'USER_EMAIL=' + sympa_soap['OWNER'],
                                                        'createList',
                                                        (name, subject, template, description, topics)
                                                        )
        else:
            return 'Server not defined'
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
