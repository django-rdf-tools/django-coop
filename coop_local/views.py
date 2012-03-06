# -*- coding:utf-8 -*-

from django.shortcuts import render_to_response, redirect
from coop_local.models import Organization
from django.template import RequestContext

def org_list(request):
    context = {}
    context['org_list'] = Organization.objects.filter(active=True).order_by('secteur_fse','title')
    return render_to_response('org/org_list.html',context,RequestContext(request))
