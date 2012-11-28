# -*- coding:utf-8 -*-
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import json
from coop.models import rdfGraphAll
from django.core.exceptions import ImproperlyConfigured
from django.contrib import admin
from django.db.models.loading import get_model


def rdf_import(request):
    rdict = {'models': [], 'pes': settings.PES_HOST}
    models = ['organization', 'article', 'event', 'exchange']
    for name in models:
        cls = get_model('coop_local', name)
        rdict['models'].append({'name': name, 'label': cls.Meta.verbose_name_plural})
    return render_to_response('admin/rdf_import.html', rdict, RequestContext(request))
