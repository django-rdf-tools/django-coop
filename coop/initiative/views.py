# # -*- coding:utf-8 -*-
# from django.views.generic import DetailView
# from coop_local.models import Initiative, Membre, Engagement
# 
# class ISDetailView(DetailView):
#     
#     context_object_name = "initiative"
#     model = Initiative
#     
#     def get_context_data(self, **kwargs):
#         context = super(ISDetailView, self).get_context_data(**kwargs)
#         context['engagements'] = Engagement.objects.filter(initiative=context['object'])
#         return context
        
# -*- coding:utf-8 -*-

from django.shortcuts import render_to_response, redirect
from coop_local.models import Initiative, Membre, Engagement
from django.template import RequestContext
from django.core.urlresolvers import reverse

def ISDetailView(request,slug):
    context = {}
    initiative = Initiative.objects.get(slug=slug)
    context['object'] = initiative
    context['adresses'] = initiative.site_set.all()
    context['engagements'] = Engagement.objects.filter(initiative=context['object'])
    return render_to_response('initiative/initiative_detail.html',context,RequestContext(request))