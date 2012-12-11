# -*- coding:utf-8 -*-

from django.shortcuts import render_to_response, redirect
from coop_local.models import Organization, OrganizationCategory, Person, Location, Area
from coop_geo.models import AreaType
from django.shortcuts import render_to_response
from coop_local.models import Organization, OrganizationCategory, DeletedURI
from django.template import RequestContext
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import json
from django.core.exceptions import ImproperlyConfigured

if('coop.exchange' in settings.INSTALLED_APPS):
    from coop_local.models import Exchange

if('coop.agenda' in settings.INSTALLED_APPS):
    from coop_local.models import Event, EventCategory


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
    try:
        object = req_model.objects.get(uuid=uuid)
        return HttpResponse(object.toRdf(format), mimetype=RDF_SERIALIZATIONS[format])
    except req_model.DoesNotExist:
        object = get_object_or_404(DeletedURI, uuid=uuid)
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


from django.core import serializers


def communes(request):
    label = request.GET['term']
    qs = Location.objects.filter(city__icontains=label, is_ref_center=True)
    data = []
    for l in qs:
        item = {}
        item['label'] = l.city
        item['value'] = l.point.coords
        data.append(item)

    #data = serializers.serialize('json', qs, fields=('city','point'))

    return HttpResponse(json.dumps(data), mimetype="application/json")


def geojson(request):

    from django.contrib.gis.measure import Distance
    from django.contrib.gis.geoip import GeoIP
    from django.contrib.gis.geos import Point
    from django.contrib.gis.geos import fromstr

    #import pdb; pdb.set_trace()

    if request.GET.get('distance'):
        dist = request.GET['distance']
    else:
        dist = 20

    if request.GET.get('center'):
        print request.GET['center']
        coords = request.GET['center'].split(',')
        my_lat = coords[0]
        my_long = coords[1]
        center = fromstr('POINT(' + my_lat + " " + my_long + ')')
    else:
        g = GeoIP()
        center = g.geos(request.META['REMOTE_ADDR'])

    try:
        regiontype = AreaType.objects.get(label="Région")
        region = Area.objects.get(area_type=regiontype, reference=settings.DEFAULT_REGION_CODE)
    except:
        raise ImproperlyConfigured("No default region has been configured")

    if not center or not region.polygon.contains(center):
        center = region.default_location.point
        dist = 1000

    res = []

    for location in Location.objects.filter(point__distance_lte=(center, Distance(km=dist))):
        for loc in location.located_set.all():
            obj = loc.content_object
            if obj.__class__ == Organization and "amap" in [x.slug for x in obj.category.all()]:
                if obj.to_geoJson():
                    res.append(obj.to_geoJson())

    result = {"type": "FeatureCollection", "features":  res}
    return HttpResponse(json.dumps(result), mimetype="application/json")




if 'haystack' in settings.INSTALLED_APPS:
    from haystack.views import SearchView
    from coop_local.models import Article

    class ModelSearchView(SearchView):
        def __name__(self):
            return "ModelSearchView"

        def extra_context(self):
            extra = super(ModelSearchView, self).extra_context()

            if self.results == []:
                extra['org'] = self.form.search().models(Organization)
                if('coop.exchange' in settings.INSTALLED_APPS):
                    extra['exchange'] = self.form.search().models(Exchange)
                extra['article'] = self.form.search().models(Article)
                if('coop.agenda' in settings.INSTALLED_APPS):
                    extra['event'] = self.form.search().models(Event)
            else:
                extra['org'] = self.results.models(Organization)
                if('coop.exchange' in settings.INSTALLED_APPS):
                    extra['exchange'] = self.results.models(Exchange)
                extra['article'] = self.results.models(Article)
                if('coop.agenda' in settings.INSTALLED_APPS):
                    extra['event'] = self.results.models(Event)

            return extra
