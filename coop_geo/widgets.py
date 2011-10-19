#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.safestring import mark_safe

from floppyforms.gis import PointWidget, BaseOsmWidget

class PointWidget(PointWidget, BaseOsmWidget):
    template_name = 'gis/osm.html'
    map_width = 400
    geocode_region = settings.COOP_GEO_REGION
    geocode_bounding = settings.COOP_GEO_BOUNDING_BOX
    class Media:
        js = list(BaseOsmWidget.Media.js) +\
            ['js/jquery-1.6.2.min.js', 'js/jquery-ui-1.8.14.custom.min.js',
             'http://maps.google.com/maps/api/js?sensor=false']
        css = {'all':['css/smoothness/jquery-ui-1.8.14.custom.css']}

    map_attrs = list(BaseOsmWidget.map_attrs) + ['geocode_region',
                                                 'geocode_bounding']
