# # -*- coding:utf-8 -*-
from django.shortcuts import render_to_response, redirect
from skosxl.models import Term,Concept
from coop_local.models import Site, Initiative, Membre, Event
from django.template import RequestContext


def tag_detail(request,slug):
    context = {}
    tag = Term.objects.get(slug=slug)
    context['object'] = tag
    context['initiatives'] = Initiative.objects.filter(tags=tag)
    return render_to_response('tag_detail.html',context,RequestContext(request))
    
def tag_list(request):
    context = {}
    context['tags'] = Term.objects.all()
    return render_to_response('tag_list.html',context,RequestContext(request))
    
