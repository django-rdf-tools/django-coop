#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils import translation
from django.utils.safestring import mark_safe
from django.core.exceptions import ObjectDoesNotExist

import floppyforms.gis as ff_gis

from models import Area, Location

class LocationPointWidget(ff_gis.PointWidget, ff_gis.BaseOsmWidget):
    template_name = 'gis/osm_location.html'
    map_width = 400
    point_zoom = 18
    geocode_region = settings.COOP_GEO_REGION
    geocode_bounding = settings.COOP_GEO_BOUNDING_BOX
    class Media:
        js = ('js/jquery-1.6.2.min.js',
              'js/jquery-ui-1.8.14.custom.min.js',
              'http://maps.google.com/maps/api/js?sensor=false',
              'http://openlayers.org/api/2.10/OpenLayers.js',
              'http://www.openstreetmap.org/openlayers/OpenStreetMap.js',
              'js/MapWidget.js',)
        css = {'all':['css/smoothness/jquery-ui-1.8.14.custom.css']}

    map_attrs = list(ff_gis.BaseOsmWidget.map_attrs) + \
                ['geocode_region', 'geocode_bounding', 'point_zoom']

    def get_context_data(self):
        context = super(LocationPointWidget, self).get_context_data()
        context['areas'] = Area.get_all()
        return context

class ChooseLocationWidget(ff_gis.PointWidget, ff_gis.BaseOsmWidget):
    template_name = 'gis/osm_choose_location.html'
    map_width = 400
    point_zoom = 18
    geocode_region = settings.COOP_GEO_REGION
    geocode_bounding = settings.COOP_GEO_BOUNDING_BOX
    class Media:
        js = ('js/jquery-1.6.2.min.js',
              'js/jquery-ui-1.8.14.custom.min.js',
              'http://maps.google.com/maps/api/js?sensor=false',
              'http://openlayers.org/api/2.10/OpenLayers.js',
              'http://www.openstreetmap.org/openlayers/OpenStreetMap.js',
              'js/MapWidget.js',)
        css = {'all':['css/smoothness/jquery-ui-1.8.14.custom.css']}

    map_attrs = list(ff_gis.BaseOsmWidget.map_attrs) + \
                ['geocode_region', 'geocode_bounding', 'point_zoom']

    def __init__(self, user, *args, **kwargs):
        self.user = user
        return super(ChooseLocationWidget, self).__init__(*args, **kwargs)

    def get_context(self, name, value, attrs=None, extra_context={}):
        # Defaulting the WKT value to a blank string
        wkt, location = '', None
        if value:
            try:
                location = Location.objects.get(pk=int(value))
                wkt = location.point.wkt
            except ObjectDoesNotExist:
                pass
        context = super(ChooseLocationWidget, self).get_context(name, wkt,
                                                                attrs)
        context['location'] = ""
        if location:
            context['location'] = unicode(location)
        context['attrs']['value'] = wkt
        context['module'] = 'map_%s' % name.replace('-', '_')
        context['name'] = name
        context['ADMIN_MEDIA_PREFIX'] = settings.ADMIN_MEDIA_PREFIX
        context['LANGUAGE_BIDI'] = translation.get_language_bidi()
        return context

    def get_context_data(self):
        context = super(ChooseLocationWidget, self).get_context_data()
        #context['locations'] = Location.get_all(self.user)
        return context

class PolygonWidget(ff_gis.MultiPolygonWidget, ff_gis.BaseOsmWidget):
    template_name = 'gis/osm.html'
    map_width = 400
    areas = Area.get_all()
