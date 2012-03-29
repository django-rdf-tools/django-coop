# # -*- coding:utf-8 -*-
        
from django.shortcuts import render_to_response
from coop_local.models import Organization, Engagement, Role
from django.template import RequestContext
from django.shortcuts import get_object_or_404


def org_detail_view(request, slug):
    context = {'editable': True}
    org = get_object_or_404(Organization, slug=slug)    
    context['organization'] = org
    context['object'] = org
    #context['rss'] = org.contact.get(category=6)
    context['adresses'] = org.located.all()
    context['engagements'] = Engagement.objects.filter(organization=org)
    return render_to_response('org/org_detail.html', context, RequestContext(request))


def org_edit(request, slug):
    context = {}
    org = get_object_or_404(Organization, slug=slug)    
    context['object'] = org
    context['adresses'] = org.located.all()
    context['engagements'] = Engagement.objects.filter(organization=context['object'])
    return render_to_response('org/org_detail.html', context, RequestContext(request))
   

def org_list(request):
    context = {}
    context['org_list'] = Organization.objects.filter(active=True)
    return render_to_response('org/org_list.html', context, RequestContext(request))
        
    
def role_detail(request, slug):
    context = {}
    role = Role.objects.get(slug=slug)
    context['object'] = role
    context['engagements'] = Engagement.objects.filter(role=role).select_related('person').order_by('person__last_name')
    return render_to_response('org/role_detail.html', context, RequestContext(request))


def global_map(request):
    context = {}
    context['initiatives'] = Organization.objects.filter(active=True)
    return render_to_response('org/org_global_map.html',
                              context, RequestContext(request))
