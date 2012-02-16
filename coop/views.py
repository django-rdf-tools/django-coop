# -*- coding:utf-8 -*-

from django.shortcuts import render_to_response, redirect
from coop_local.models import Initiative, Person
from django.template import RequestContext
from django.core.urlresolvers import reverse

def home(request):
    rdict = {}
    rdict['dernieres_initiatives'] = Initiative.objects.filter(active=True)[:10]
    rdict['inscrits'] = Person.objects.all().count()    
    return render_to_response('home.html',rdict,RequestContext(request))