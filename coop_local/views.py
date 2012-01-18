# -*- coding:utf-8 -*-

# # -*- coding:utf-8 -*-
from django.shortcuts import render_to_response, redirect
from skosxl.models import Label,Concept,LabelledItem
from django.template import RequestContext

from coop_local.models import Initiative


def tag_detail(request,slug):
    context = {}
    tag = Label.objects.get(slug=slug)
    context['object'] = tag
    context['initiatives'] = Initiative.objects.filter(tags=tag)
    return render_to_response('tag_detail.html',context,RequestContext(request))

