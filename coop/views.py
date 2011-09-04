# -*- coding:utf-8 -*-

from django.shortcuts import render_to_response, redirect
from coop_local.models import Initiative, Membre
from django.template import RequestContext
from django.core.urlresolvers import reverse

def home(request):
    rdict = {}
    rdict['dernieres_initiatives'] = Initiative.objects.all()[:10]
    rdict['inscrits'] = Membre.objects.all().count()
    return render_to_response('home.html',rdict,RequestContext(request))