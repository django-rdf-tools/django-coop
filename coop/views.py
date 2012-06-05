# -*- coding:utf-8 -*-

from django.shortcuts import render_to_response, redirect
from coop_local.models import Organization, Person
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import Http404

if('coop.exchange' in settings.INSTALLED_APPS):
    from coop_local.models import Exchange


def home(request):
    rdict = {}
    rdict['dernieres_initiatives'] = Organization.objects.filter(active=True)[:10]    
    if('coop.exchange' in settings.INSTALLED_APPS):
        rdict['dernieres_annonces'] = Exchange.objects.all()[:10]
    return render_to_response('home.html', rdict, RequestContext(request))


def d2r_mapping(request, mode):
    if(request.META['REMOTE_ADDR'] in settings.INTERNAL_IPS and mode in ['view', 'export']):
        db = settings.DATABASES['default']
        rdict = {}
        rdict['mode'] = mode
        rdict['namespaces'] = settings.RDF_NAMESPACES
        rdict['d2r_baseURI'] = settings.D2RQ_ROOT
        rdict['d2r_niceURI'] = settings.D2RQ_NICE_URL
        rdict['d2r_port'] = settings.D2RQ_PORT
        rdict['d2r_site_name'] = unicode(settings.SITE_TITLE) + u' : RDF mapping'
        rdict['d2rq_username'] = db['USER']
        rdict['d2rq_password'] = db['PASSWORD']
        rdict['d2rq_db_name'] = db['NAME']
        rdict['d2rq_db_port'] = db['PORT'] if db['PORT'] != '' else 5432
        rdict['d2rq_db_host'] = db['HOST'] if db['HOST'] != '' else 'localhost'
    else:
        raise Http404    
    return render_to_response('d2r/mapping.ttl', rdict, RequestContext(request))
