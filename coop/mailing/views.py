# -*- coding:utf-8 -*-
# Create your views here.

from django.http import HttpResponse
from soap import info as soap_info, lists


def list(request, name):
    """
    :name MailingList name
    """
    # TODO il faut contruite la liste a partir de la 
    return HttpResponse('clo claude.huchet@quinode.fr')
