#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.db import models

class Location(models.Model):
    """Location: a named point or/and polygon"""
    label = models.CharField(max_length=150, verbose_name=_(u"label"))
    point = models.PointField(_(u"point"), srid=settings.EPSG_PROJECTION,
                              blank=True, null=True)
    polygon = models.PolygonField(_(u"polygon"), srid=settings.EPSG_PROJECTION,
                                  blank=True, null=True)
    objects = models.GeoManager()

    def save(self, *args, **kwargs):
        if not self.point and not self.polygon:
            raise ValidationError(u"You must set a point or a polygon.")
        return super(Location, self).save(*args, **kwargs)
