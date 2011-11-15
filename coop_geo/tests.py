#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.gis.geos import GEOSGeometry

from coop_geo.models import Location, Area

class LocationTest(TestCase):
    def setUp(self):
        pass

    def test_set_creation(self):
        with self.assertRaises(ValidationError):
            location = Location(label=u'Test', point=None)
            location.save()

class AreaTest(TestCase):
    def setUp(self):
        pass

    def test_set_creation(self):
        polygon = GEOSGeometry('SRID=4326;POLYGON((-8.88 53.81,-1.41 55.84,'\
                               '-5.54 53.29,0.34 54.69, -8.88 53.81))')
        main_area = Area(label=u'Test', polygon=polygon)
        main_area.save()
        with self.assertRaises(ValidationError):
            main_area.parent = main_area
            main_area.save()

    def test_levels(self):
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

