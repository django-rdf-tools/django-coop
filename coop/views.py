# -*- coding:utf-8 -*-

from django.shortcuts import render_to_response, redirect
from coop_local.models import Initiative, Membre
from django.template import RequestContext
from django.core.urlresolvers import reverse
from skosxl.models import Term

def home(request):
    rdict = {}
    rdict['dernieres_initiatives'] = Initiative.objects.filter(active=True)[:10]
    rdict['tags'] = Term.objects.all().order_by('count')
    rdict['inscrits'] = Membre.objects.all().count()
    return render_to_response('home.html',rdict,RequestContext(request))