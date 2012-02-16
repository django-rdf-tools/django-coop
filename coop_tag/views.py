# -*- coding:utf-8 -*-
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from coop_tag.models import Ctag, CtaggedItem
from coop_local.models import Organization

# pourrait faire partie d'une appli coop-tags
def tag_detail(request,slug):
    context = {}
    tag = Ctag.objects.get(slug=slug)
    context['object'] = tag
    context['initiatives'] = Organization.objects.filter(tags=tag)    
    return render_to_response('tag_detail.html',context,RequestContext(request))

