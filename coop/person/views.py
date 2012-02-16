# # -*- coding:utf-8 -*-
from django.shortcuts import render_to_response, redirect
from coop_local.models import Organization, Person
from django.template import RequestContext
from django.core.urlresolvers import reverse

def perso(request):
    context = {}
    context['user'] = request.user
    return render_to_response('person/panel.html',context,RequestContext(request))