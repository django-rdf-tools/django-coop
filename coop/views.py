# -*- coding:utf-8 -*-

from django.shortcuts import render_to_response, redirect
from coop_local.models import Organization, Person
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.conf import settings

def home(request):
    rdict = {}
    rdict['dernieres_initiatives'] = Organization.objects.filter(active=True)[:10]
    rdict['inscrits'] = Person.objects.all().count()
    return render_to_response('home.html',rdict,RequestContext(request))