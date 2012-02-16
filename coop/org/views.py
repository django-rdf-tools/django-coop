# # -*- coding:utf-8 -*-
        
from django.shortcuts import render_to_response, redirect
from coop_local.models import Initiative, Person, Engagement, Role
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

def org_detail_view(request,slug):
    context = {}
    org = get_object_or_404(Initiative,slug=slug)    
    context['object'] = org
    #context['rss'] = org.contact.get(category=6)
    context['adresses'] = org.located.all()
    context['engagements'] = Engagement.objects.filter(initiative=context['object'])
    return render_to_response('org/org_detail.html',context,RequestContext(request))
    

def list(request):
    context = {}
    context['liste_initiatives'] = Initiative.objects.filter(active=True).order_by('secteur_fse','title')#FIXME ah là il faut surclasser
    return render_to_response('org/org_list.html',context,RequestContext(request))
        
    
def role_detail(request,slug):
    context = {}
    role = Role.objects.get(slug=slug)
    context['object'] = role
    context['engagements'] = Engagement.objects.filter(role=role).select_related('membre').order_by('membre__last_name')
    return render_to_response('org/role_detail.html',context,RequestContext(request))

def global_map(request):
    context = {}
    context['initiatives'] = Initiative.objects.filter(active=True)
    return render_to_response('org/org_global_map.html',
                              context, RequestContext(request))
