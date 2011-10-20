#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.safestring import mark_safe

import floppyforms.gis as ff_gis

from models import Area

class PointWidget(ff_gis.PointWidget, ff_gis.BaseOsmWidget):
    template_name = 'gis/osm_point.html'
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

class PolygonWidget(ff_gis.PolygonWidget, ff_gis.BaseOsmWidget):
    template_name = 'gis/osm.html'
    map_width = 400
    areas = Area.get_all()
