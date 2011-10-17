#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from coop_geo.models import Location
from django.core.exceptions import ValidationError

class LocationTest(TestCase):
    def setUp(self):
        pass

    def test_set_creation(self):
        with self.assertRaises(ValidationError):
            location = Location(name=u'Test', point=None, polygon=None)
            location.save()
