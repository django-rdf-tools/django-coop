# # -*- coding:utf-8 -*-
from django.shortcuts import render_to_response, redirect
from skosxl.models import Label,Concept
from coop_local.models import Site, Initiative, Membre
from django.template import RequestContext


def tag_detail(request,slug):
    context = {}
    tag = Label.objects.get(slug=slug)
    context['object'] = tag
    context['initiatives'] = Initiative.objects.filter(tags=tag)
    return render_to_response('tag_detail.html',context,RequestContext(request))
    
def tag_list(request):
    context = {}
    context['tags'] = Label.objects.all()
    return render_to_response('tag_list.html',context,RequestContext(request))
    
