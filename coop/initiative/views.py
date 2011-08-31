# -*- coding:utf-8 -*-
from django.views.generic import DetailView
from coop_local.models import Initiative, Membre, Engagement

class ISDetailView(DetailView):
    
    context_object_name = "initiative"
    model = Initiative
    
    def get_context_data(self, **kwargs):
        context = super(ISDetailView, self).get_context_data(**kwargs)
        print context
        context['engagements'] = Engagement.objects.filter(initiative=context['object'])
        return context