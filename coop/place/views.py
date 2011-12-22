# # -*- coding:utf-8 -*-
from django.shortcuts import render_to_response, redirect
from coop_local.models import Site, Initiative, Membre
from django.template import RequestContext
from django.core.urlresolvers import reverse

def detail(request,uuid):
    context = {}
    lieu = Site.objects.get(uuid=uuid)
    context['object'] = lieu
    context['initiative'] = lieu.initiative
    return render_to_response('place/place_detail.html',context,RequestContext(request))