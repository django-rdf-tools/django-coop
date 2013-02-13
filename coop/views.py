# -*- coding:utf-8 -*-
from django.shortcuts import render_to_response
from coop_local.models import Organization, OrganizationCategory,  Location, Area
from coop_geo.models import AreaType
from coop_local.models import  DeletedURI
from django.template import RequestContext
from django.conf import settings
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import get_object_or_404
import json
import simplejson
from django.core.exceptions import ImproperlyConfigured
from django.contrib.gis.geos import fromstr
import logging
from django.contrib.sites.models import Site

log = logging.getLogger()

if('coop.exchange' in settings.INSTALLED_APPS):
    from coop_local.models import Exchange

if('coop.agenda' in settings.INSTALLED_APPS):
    from coop_local.models import Event, EventCategory



# Util function for views. The region is used to center views using catograpy
def default_region():
    code_region = getattr(settings, 'DEFAULT_REGION_CODE', 83)
    try:
        regiontype = AreaType.objects.get(label="Région")
        region = Area.objects.get(area_type=regiontype, reference=code_region)
    except:
        log.debug("No default region has been configured")
        region = None
        # raise ImproperlyConfigured("No default region has been configured")
    return region


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
        qs = Event.objects.filter(category=cat)  

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




# TODO: how to have extra parametre to customise  the geoJson ?
def geojson(request, model):
    """
        The main view to get geoJson features from Organization model
        get query could be (thre is no dependance between queries)
        ?id= an Organization id
        ?category=a category slug (category are available for Organization, Event, Project, ..)
        ?dist=dist&center=x,y  filter around a point
        ?zone=ref,type  filter for a 'zone', where 'ref' is the 'reference' fieds value and 'type' is
        the area_type.txt_idx value
        ?geotype= 'all' | 'pref' | 'locations'| 'areas' (could 'zone' for project)
        If no query is specified, it returns all kind of  geoJson features for all active instance 
        of the model Model and usef the method pref_geoJson to build geoJson features;
        Take care that 'id' and 'category' requests are combine

    """
    from django.contrib.gis.measure import Distance
    from coop_local.models import Area
    from coop_geo.models import AreaType

    model_type = get_model('coop_local', model)
    if not model_type:
        raise Http404
    else:
        if not hasattr(model_type, 'geom_manager'):
            raise Http404

    # default values
    try:        
        qs = model_type.geom_manager.filter(active=True)
    except:
        qs = model_type.geom_manager.all()
    geo_type = 'pref'

    get = request.GET
    if  get:
        # filter about organizations
        if get.get('id'):
            qs = qs.filter(id=get.get('id'))
        if get.get('category'):
            slug = get.get('category')
            if hasattr(model_type, 'category'):
                try:
                    cat_type = model_type.category.field.related.parent_model
                    cat = cat_type.objects.get(slug=slug)
                    qs = qs.filter(category=cat)
                except cat_type.DoesNotExist:
                    pass
        # geom filter
        if get.get('dist'):
            dist = get.get('dist')
            coords = get.get('center').split(',')
            my_lat = coords[0]
            my_long = coords[1]
            center = fromstr('POINT(' + my_lat + " " + my_long + ')')
            qs = qs.filter(pref_address__point__distance_lte=(center, Distance(km=dist)))
        if get.get('zone'):
            zone = get.get('zone').split(',')
            ref = zone[0]
            ztype = zone[1]
            try:
                at = AreaType.objects.get(txt_idx=ztype)
                a = Area.objects.filter(reference=ref, area_type=at)[0]  # should be unique
                qs = qs.filter(pref_address__point__contained=a.polygon)
            except (AreaType.DoesNotExist, IndexError):
                print "cannot filter on zone"

        # filter about geoJson features
        if get.get('geotype'):
            geo_type = get.get('geotype')

    res = []
    for obj in qs:
        if settings.COOP_USE_SITES:
            site = Site.objects.get_current()
            if site in obj.sites.all():
                res.extend(getattr(obj, geo_type + '_geoJson')())
        else:
            res.extend(getattr(obj, geo_type + '_geoJson')())

    # On met au moins une region (c'est mieux qu'une erreur)
    if res == []:
        region = default_region()
        if region:
            gjson = region.geoJson()
            gjson["properties"]["label"] = region.label.encode("utf-8")
            res = [gjson]

    result = {"type": "FeatureCollection", "features":  res}
    return HttpResponse(json.dumps(result), mimetype="application/json")


# TODO: to be removed... only used in AllianceProvence
def geojson_amap(request):
    from django.contrib.gis.measure import Distance
    from django.contrib.gis.geoip import GeoIP
    from django.contrib.gis.geos import fromstr
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
        g = GeoIP(path=settings.PROJECT_PATH + '/config/GEO/')
        center = g.geos(request.META['REMOTE_ADDR'])

    region = default_region()
    if not center or not region.polygon.contains(center):
        center = region.default_location.point
        dist = 1000

    res = []

    for location in Location.objects.filter(point__distance_lte=(center, Distance(km=dist))):
        for loc in location.located_set.all():
            obj = loc.content_object
            if obj.__class__ == Organization and "amap" in [x.slug for x in obj.category.all()]:
                res.extend(obj.pref_geoJson())
 
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

            # the call to .__dict__['query'].get_results() is a work around due 
            # the issue #575 (on django-haystack project)
            search = self.form.search()
            results = self.results
            if 'whoosh' in settings.HAYSTACK_CONNECTIONS['default']['ENGINE']:


                if results.models(Organization).count() == 0:
                    extra['org'] = search.models(Organization).__dict__['query'].get_results()
                else:
                    extra['org'] = results.models(Organization).__dict__['query'].get_results()

                if('coop.exchange' in settings.INSTALLED_APPS):
                    if results.models(Exchange).count() == 0:
                        extra['exchange'] = search.models(Exchange).__dict__['query'].get_results()
                    else:
                        extra['exchange'] = results.models(Exchange).__dict__['query'].get_results()

                if results.models(Article).count() == 0:
                    extra['article'] = search.models(Article).__dict__['query'].get_results()
                else:
                    extra['article'] = results.models(Article).__dict__['query'].get_results()

                if('coop.agenda' in settings.INSTALLED_APPS):
                    if results.models(Event).count() == 0:
                        extra['event'] = search.models(Event).__dict__['query'].get_results()
                    else:
                        extra['event'] = results.models(Event).__dict__['query'].get_results()

            else:

                if results.models(Organization).count() == 0:
                    extra['org'] = search.models(Organization)
                else:
                    extra['org'] = results.models(Organization)

                if('coop.exchange' in settings.INSTALLED_APPS):
                    if results.models(Exchange).count() == 0:
                        extra['exchange'] = search.models(Exchange)
                    else:
                        extra['exchange'] = results.models(Exchange)

                if results.models(Article).count() == 0:
                    extra['article'] = search.models(Article)
                else:
                    extra['article'] = results.models(Article)

                if('coop.agenda' in settings.INSTALLED_APPS):
                    if results.models(Event).count() == 0:
                        extra['event'] = search.models(Event)       
                    else:
                        extra['event'] = results.models(Event)

            return extra


    class SiteModelSearchView(ModelSearchView):
        def __name__(self):
            return "SiteModelSearchView"

        def __init__(self, *args, **kwargs):
            # Needed to switch out the default form class.
            if not 'site' in kwargs:
                self.site = Site.objects.get_current()
            else:
                site = kwargs.pop('site')
                if site:
                    self.site = site
                else:
                    self.site = Site.objects.get_current()
            super(SiteModelSearchView, self).__init__(*args, **kwargs)

        def build_form(self, form_kwargs=None):
            form = super(SiteModelSearchView, self).build_form(form_kwargs)
            if hasattr(form, 'set_site'):
                form.set_site(self.site)
            return form

        def extra_context(self):
            extra = super(ModelSearchView, self).extra_context()
            extra['site'] = self.site
            return extra
