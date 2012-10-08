# -*- coding:utf-8 -*-

from django.shortcuts import render_to_response, redirect
from coop_local.models import Event, EventCategory, Organization, OrganizationCategory, Person
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import json

if('coop.exchange' in settings.INSTALLED_APPS):
    from coop_local.models import Exchange


def home(request):
    rdict = {}
    rdict['dernieres_initiatives'] = Organization.objects.filter(active=True)[:10]
    if('coop.exchange' in settings.INSTALLED_APPS):
        rdict['dernieres_annonces'] = Exchange.objects.all()[:10]
    return render_to_response('home.html', rdict, RequestContext(request))


# def d2r_mapping(request, mode):
#     if(request.META['REMOTE_ADDR'] in settings.INTERNAL_IPS and mode in ['view', 'export']):
#         db = settings.DATABASES['default']
#         rdict = {}
#         rdict['mode'] = mode
#         rdict['namespaces'] = settings.RDF_NAMESPACES
#         rdict['d2r_baseURI'] = settings.D2RQ_ROOT
#         rdict['d2r_niceURI'] = 'http://' + settings.DEFAULT_URI_DOMAIN + '/'
#         rdict['d2r_port'] = settings.D2RQ_PORT
#         rdict['d2r_site_name'] = unicode(settings.SITE_TITLE) + u' : RDF mapping'
#         rdict['d2rq_username'] = db['USER']
#         rdict['d2rq_password'] = db['PASSWORD']
#         rdict['d2rq_db_name'] = db['NAME']
#         rdict['d2rq_db_port'] = db['PORT'] if db['PORT'] != '' else 5432
#         rdict['d2rq_db_host'] = db['HOST'] if db['HOST'] != '' else 'localhost'
#     else:
#         raise Http404
#     return render_to_response('d2r/mapping.ttl', rdict, RequestContext(request))


from django.db import models
from coop.models import StaticURIModel
from django.db.models.loading import get_model

urimodels = dict((m.__name__.lower(), m.__module__.split('.')[0]) for m in models.get_models() if m.__mro__.__contains__(StaticURIModel))
# To be compliante with the dynamic loading process
for k in urimodels:
    if urimodels[k] == 'coop':
        urimodels[k] = 'coop_local'


RDF_SERIALIZATIONS = {
    'nt': 'text/plain',
    'n3': 'text/n3',
    'ttl': 'text/turtle',
    'xml': 'application/rdf+xml',
    'json': 'application/json',
    'trix': 'application/trix'
}


# smallest data API ever
def get_rdf(request, model, uuid, format):
    req_model = get_model(urimodels[model], model)
    object = get_object_or_404(req_model, uuid=uuid)
    return HttpResponse(object.toRdf(format), mimetype=RDF_SERIALIZATIONS[format])


def SentryHandler500(request):
    from django.template import Context, loader
    from django.http import HttpResponseServerError

    t = loader.get_template('500.html')  # You need to create a 500.html template.
    return HttpResponseServerError(t.render(Context({
        'request': request,
        'STATIC_URL': settings.STATIC_URL,
    })))


def geojson_objects(request, what, criteria):
    positions = {}
    if what == "org":
        cat = OrganizationCategory.objects.get(slug=criteria)
        qs = Organization.objects.filter(category=cat)
        for org in qs:
            for loc in org.locations():
                if not loc.city in positions:
                    positions[loc.city] = {
                        "type": "Feature",
                        "properties": {
                            #"name": cl.commune.nom,
                            "popupContent": u"<h4>" + loc.city + u"</h4><p class='org'><a href='" + org.get_absolute_url() + u"'>" + org.label() + u"</a></p>"
                            },
                        "geometry": {
                            "type": "Point",
                            #"coordinates": [str(loc.point.x), str(loc.point.y)]
                            "coordinates": [loc.point.x, loc.point.y]

                            }
                        }

                else:
                    positions[loc.city]["properties"]["popupContent"] += u"\n<p class='geo_item'><a href='" + \
                            org.get_absolute_url() + u"'>" + org.label() + u"</a></p>"
    elif what == "event":
        cat = EventCategory.objects.get(slug=criteria)
        qs = Event.objects.filter(event_type=cat)  # TODO rename category !!

        for event in qs:
            loc = event.location
            if loc and not loc.city in positions:
                positions[loc.city] = {
                    "type": "Feature",
                    "properties": {
                        "popupContent": u"<h4>" + loc.city + u"</h4><p class='org'><a href='" + event.get_absolute_url() + u"'>" + event.title + u"</a></p>"
                        },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [loc.point.x, loc.point.y]

                        }
                    }
            else:
                positions[loc.city]["properties"]["popupContent"] += u"\n<p class='geo_item'><a href='" + \
                            event.get_absolute_url() + u"'>" + event.title + u"</a></p>"

    result = {"type": "FeatureCollection", "features": positions.values()}
    return HttpResponse(json.dumps(result), mimetype="application/json")

