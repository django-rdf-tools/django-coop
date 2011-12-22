#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from django.utils import simplejson as json
from django.utils.http import urlquote
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse, resolve
from django.contrib.auth.models import User, Permission
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos.collections import GeometryCollection

from coop_geo.models import Location, Area, AreaRelations, RELATION_TYPES

DEFAULT_RELATION_TYPE = RELATION_TYPES[0][0]

class AreaTest(TestCase):
    def setUp(self):
        pass

    def test_set_creation(self):
        polygon = GEOSGeometry('SRID=4326;MULTIPOLYGON(((0 0,10 0,10 10,0 10,'\
                               '0 0)))')
        main_area = Area(label=u'Test', polygon=polygon)
        main_area.save()
        self.assertEqual(main_area.default_location.point,
                         GEOSGeometry('SRID=4326;POINT (5 5)'))

    def test_relations_creation(self):
        polygon_low = GEOSGeometry('SRID=4326;MULTIPOLYGON((('\
                                        '0 0,10 0,10 10,0 10,0 0)))')
        polygon_high = GEOSGeometry('SRID=4326;MULTIPOLYGON((('\
                                        '0 10,10 10,10 20,0 20,0 10)))')
        polygon_full = GEOSGeometry('SRID=4326;MULTIPOLYGON((('\
                               '0 0,10 0,10 10,10 20,0 20,0 10, 0 0)))')
        polygon_default = GEOSGeometry('SRID=4326;MULTIPOLYGON((('\
                                        '0 0,1 0,1 2,0 2,0 0)))')
        area_low = Area.objects.create(label=u'Test low', polygon=polygon_low)
        area_high = Area.objects.create(label=u'Test high',
                                        polygon=polygon_high)
        area_full = Area.objects.create(label=u"Test full", update_auto=True,
                                        polygon=polygon_default)
        with self.assertRaises(ValidationError):
            area_full.add_parent(area_full, DEFAULT_RELATION_TYPE)
        with self.assertRaises(ValidationError):
            area_full.add_child(area_full, DEFAULT_RELATION_TYPE)
        area_full.add_child(area_low, DEFAULT_RELATION_TYPE)
        area_full.add_child(area_high, DEFAULT_RELATION_TYPE)
        self.assertEqual(AreaRelations.objects.filter(
                         parent=area_full).count(), 2)
        self.assertEqual(AreaRelations.objects.filter(
                         child=area_full).count(), 0)
        self.assertEqual(AreaRelations.objects.filter(
                         child=area_low).count(), 1)
        self.assertEqual(area_full.polygon.difference(polygon_full).area, 0)
        self.assertEqual(polygon_full.difference(area_full.polygon).area, 0)
        area_low.polygon = GEOSGeometry('SRID=4326;MULTIPOLYGON((('\
                                        '0 -10,10 -10,10 10,0 10,0 -10)))')
        area_low.save()
        area_full = Area.objects.get(pk=3)
        polygon_full_2 = GEOSGeometry('SRID=4326;MULTIPOLYGON((('\
                                         '0 -10,10 -10,10 20,0 20,0 -10)))')
        self.assertEqual(area_full.polygon.difference(polygon_full_2).area, 0)
        self.assertEqual(polygon_full_2.difference(area_full.polygon).area, 0)

    def test_relations_levels(self):
        polygon = GEOSGeometry('SRID=4326;MULTIPOLYGON(((-8.88 53.81'\
                ',-1.41 55.84,-5.54 53.29,0.34 54.69, -8.88 53.81)))')
        """
        area_1
        > area_2
        > > area_3
        > > > area_4
        > > > area_6
        > > area_8
        > area_5
        > > area_7
        """
        area_1 = Area.objects.create(label=u'Area 1', polygon=polygon)
        area_2 = Area.objects.create(label=u'Area 2', polygon=polygon)
        area_1.add_child(area_2, DEFAULT_RELATION_TYPE)
        area_3 = Area.objects.create(label=u'Area 3', polygon=polygon)
        area_3.add_parent(area_2, DEFAULT_RELATION_TYPE)
        area_4 = Area.objects.create(label=u'Area 4', polygon=polygon)
        area_5 = Area.objects.create(label=u'Area 5', polygon=polygon)
        area_5.add_parent(area_1, DEFAULT_RELATION_TYPE)
        area_6 = Area.objects.create(label=u'Area 6', polygon=polygon)
        area_3.add_childs([area_4, area_6], DEFAULT_RELATION_TYPE)
        area_7 = Area.objects.create(label=u'Area 7', polygon=polygon)
        area_5.add_childs([area_7], DEFAULT_RELATION_TYPE)
        area_8 = Area.objects.create(label=u'Area 8', polygon=polygon)
        area_2.add_child(area_8, DEFAULT_RELATION_TYPE)
        self.assertEqual(area_1.level, 0)
        self.assertEqual(area_2.level, 1)
        self.assertEqual(area_3.level, 2)
        self.assertEqual(area_4.level, 3)
        self.assertEqual(area_5.level, 1)
        self.assertEqual(area_6.level, 3)
        self.assertEqual(area_7.level, 2)
        self.assertEqual(area_8.level, 2)
        # reinitialise
        for idx in xrange(1,9):
            locals()['area_%d'%idx]._level = None
        areas = Area.get_all()
        self.assertEqual(areas, [area_1, area_2, area_3, area_4, area_6,
                                 area_8, area_5, area_7])
        areas_dct = {1:areas[0],
                     2:areas[1],
                     3:areas[2],
                     4:areas[3],
                     6:areas[4],
                     8:areas[5],
                     5:areas[6],
                     7:areas[7],
                     } # for readability
        self.assertEqual(areas_dct[1].level, 0)
        self.assertEqual(areas_dct[2].level, 1)
        self.assertEqual(areas_dct[3].level, 2)
        self.assertEqual(areas_dct[4].level, 3)
        self.assertEqual(areas_dct[5].level, 1)
        self.assertEqual(areas_dct[6].level, 3)
        self.assertEqual(areas_dct[7].level, 2)
        self.assertEqual(areas_dct[8].level, 2)

        self.assertEqual(areas_dct[1].leaf, True)
        self.assertEqual(areas_dct[2].leaf, True)
        self.assertEqual(areas_dct[3].leaf, True)
        self.assertEqual(areas_dct[6].end_leaf, 1)
        self.assertEqual(areas_dct[8].end_leaf, 1)
        self.assertEqual(areas_dct[5].leaf, True)
        self.assertEqual(areas_dct[7].end_leaf, 2)

class LocationTest(TestCase):
    def setUp(self):
        pass

    def _log_as_locationadmin(self):
        if not hasattr(self, 'locationadmin') or not self.locationadmin:
            self.locationadmin = User.objects.create_user('locationadmin',
                                                  'locationadmin@noname.org',
                                                  'locationadmin')
            self.locationadmin.is_staff = True
            can_add_location = Permission.objects.get(
                                    content_type__app_label='coop_geo',
                                    codename='add_location')
            self.locationadmin.user_permissions.add(can_add_location)
            self.locationadmin.save()
        self.client.login(username='locationadmin', password='locationadmin')

    def test_set_creation(self):
        with self.assertRaises(ValidationError):
            location = Location(label=u'Test', point=None, area=None)
            location.save()
        point = GEOSGeometry('SRID=4326;POINT(-8.88 53.81)')
        location = Location(adr1=u'Test point', point=point, area=None)
        location.save()
        self.assertEqual(location.adr1, location.label)
        polygon = GEOSGeometry('SRID=4326;MULTIPOLYGON(((-8.88 53.81,'\
                 '-1.41 55.84,-5.54 53.29,0.34 54.69, -8.88 53.81)))')
        area = Area(label=u'Test', polygon=polygon)
        area.save()
        location = Location.objects.create(label=u'Test point', point=None,
                                           area=area)
        location.save()

    def test_json_list(self):
        point = GEOSGeometry('SRID=4326;POINT(-8.88 53.81)')
        location = Location.objects.create(label=u'Test', point=point,
                        area=None, city=u'Paris', adr1=u'Rue de la liberté')
        url = reverse('json_location',
            kwargs={'city': 'paris', 'address':urlquote(u'rue de la liberté')},
            current_app='coop_geo',)
        response = self.client.get(url)
        self.assertNotEqual(200, response.status_code)
        self._log_as_locationadmin()
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response['Content-Type'], 'application/json')
        json_response = json.loads(response.content)
        self.assertEqual(len(json_response), 1)

