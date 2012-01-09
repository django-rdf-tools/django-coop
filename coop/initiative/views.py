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
        
from django.shortcuts import render_to_response, redirect
from coop_local.models import Initiative, Membre, Engagement, Role, Site
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

def ISDetailView(request,slug):
    context = {}
    initiative = get_object_or_404(Initiative,slug=slug)    
    context['object'] = initiative
    context['rss'] = initiative.rss
    context['adresses'] = initiative.located.all()
    context['engagements'] = Engagement.objects.filter(initiative=context['object'])
    return render_to_response('initiative/initiative_detail.html',context,RequestContext(request))
    

def list(request):
    context = {}
    context['liste_initiatives'] = Initiative.objects.filter(active=True).order_by('secteur_fse','title')#FIXME ah là il faut surclasser
    return render_to_response('initiative/initiative_list.html',context,RequestContext(request))
        
    
def role_detail(request,slug):
    context = {}
    role = Role.objects.get(slug=slug)
    context['object'] = role
    context['engagements'] = Engagement.objects.filter(role=role).select_related('membre').order_by('membre__nom')
    return render_to_response('initiative/role_detail.html',context,RequestContext(request))

def global_map(request):
    context = {}
    context['initiatives'] = Initiative.objects.filter(active=True)
    return render_to_response('initiative/initiative_global_map.html',
                              context, RequestContext(request))
