#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos.collections import GeometryCollection

from coop_geo.models import Location, Area, AreaRelations, RELATION_TYPES

DEFAULT_RELATION_TYPE = RELATION_TYPES[0][0]

class AreaTest(TestCase):
    def setUp(self):
        pass

    def test_set_creation(self):
        polygon = GEOSGeometry('SRID=4326;POLYGON((0 0,10 0,10 10,0 10,'\
                               '0 0))')
        main_area = Area(label=u'Test', polygon=polygon)
        main_area.save()
        self.assertEqual(main_area.default_location.point,
                         GEOSGeometry('SRID=4326;POINT (5 5)'))

    def test_relations_creation(self):
        polygon_low = GEOSGeometry('SRID=4326;POLYGON(('\
                                        '0 0,10 0,10 10,0 10,0 0))')
        polygon_high = GEOSGeometry('SRID=4326;POLYGON(('\
                                        '0 10,10 10,10 20,0 20,0 10))')
        polygon_full = GEOSGeometry('SRID=4326;POLYGON(('\
                               '0 0,10 0,10 10,10 20,0 20,0 10, 0 0))')
        polygon_default = GEOSGeometry('SRID=4326;POLYGON(('\
                                        '0 0,1 0,1 2,0 2,0 0))')
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
        area_low.polygon = GEOSGeometry('SRID=4326;POLYGON(('\
                                        '0 -10,10 -10,10 10,0 10,0 -10))')
        area_low.save()
        self.assertEqual(area_full.polygon.difference(
               GEOSGeometry('SRID=4326;POLYGON(('\
                            '0 -10,10 -10,10 20,0 20,0 -10))')).area, 0)
    '''
    def test_relations_levels(self):
        polygon = GEOSGeometry('SRID=4326;POLYGON((-8.88 53.81,-1.41 55.84,'\
                               '-5.54 53.29,0.34 54.69, -8.88 53.81))')
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
        area_1 = Area(label=u'Area 1', polygon=polygon)
        area_1.save()
        area_2 = Area(label=u'Area 2', polygon=polygon, parent=area_1)
        area_2.save()
        area_3 = Area(label=u'Area 3', polygon=polygon, parent=area_2)
        area_3.save()
        area_4 = Area(label=u'Area 4', polygon=polygon, parent=area_3)
        area_4.save()
        area_5 = Area(label=u'Area 5', polygon=polygon, parent=area_1)
        area_5.save()
        area_6 = Area(label=u'Area 6', polygon=polygon, parent=area_3)
        area_6.save()
        area_7 = Area(label=u'Area 7', polygon=polygon, parent=area_5)
        area_7.save()
        area_8 = Area(label=u'Area 8', polygon=polygon, parent=area_2)
        area_8.save()
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
'''
class LocationTest(TestCase):
    def setUp(self):
        pass

    def test_set_creation(self):
        with self.assertRaises(ValidationError):
            location = Location(label=u'Test', point=None, area=None)
            location.save()
        point = GEOSGeometry('SRID=4326;POINT(-8.88 53.81)')
        location = Location(label=u'Test point', point=point, area=None)
        location.save()
        polygon = GEOSGeometry('SRID=4326;POLYGON((-8.88 53.81,-1.41 55.84,'\
                               '-5.54 53.29,0.34 54.69, -8.88 53.81))')
        area = Area(label=u'Test', polygon=polygon)
        area.save()
        location = Location.objects.create(label=u'Test point', point=None,
                                           area=area)
        location.save()

