# -*- coding: utf-8 -*-
from SOAPpy import WSDL, faultType
from django.conf import settings
from logging import getLogger
logger = getLogger('coop')

try:
    _server = WSDL.Proxy(settings.SYMPA_SOAP['WSDL'])
except Exception, e:
    logger.warning(u"Cannot find find Sympa server - %s" % e)


def lists():
    try:
        return _server.authenticateRemoteAppAndRun(settings.SYMPA_SOAP['APPNAME'], settings.SYMPA_SOAP['PASSWORD'], settings.SYMPA_SOAP['OWNER'], 'lists')
    except faultType, e:
        return e.faultstring


def info(name):
    try:
        return _server.authenticateRemoteAppAndRun(settings.SYMPA_SOAP['APPNAME'], settings.SYMPA_SOAP['PASSWORD'], settings.SYMPA_SOAP['OWNER'], 'info', (name,))
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
        return _server.authenticateRemoteAppAndRun(settings.SYMPA_SOAP['APPNAME'], settings.SYMPA_SOAP['PASSWORD'], settings.SYMPA_SOAP['OWNER'], 'createList', (name, subject, template, description, topics))
    except faultType, e:
        return e.faultstring


def close_list(name):
    try:
        return _server.authenticateRemoteAppAndRun(settings.SYMPA_SOAP['APPNAME'], settings.SYMPA_SOAP['PASSWORD'], settings.SYMPA_SOAP['OWNER'], 'closeList', (name,))
    except faultType, e:
        return e.faultstring
