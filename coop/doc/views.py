
# -*- coding:utf-8 -*-
from django.conf import settings
from django.shortcuts import render_to_response, redirect
from coop_local.models import DocResource
from django.template import RequestContext
from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponse
import json


def resource_detail(request, slug):
    context = {}
    context['item'] = get_object_or_404(DocResource, slug=slug)
    return render_to_response('doc/resource_detail.html', context, RequestContext(request))
