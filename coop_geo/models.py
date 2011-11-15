#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.gis.db import models

class Location(models.Model):
    """Location: a named point or/and polygon entered by an administrator"""
    label = models.CharField(max_length=150, verbose_name=_(u"label"))
    point = models.PointField(_(u"point"),
                              srid=settings.COOP_GEO_EPSG_PROJECTION)
    owner = models.ForeignKey(User, verbose_name=_(u'owner'), blank=True,
                              null=True)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.label

    @classmethod
    def get_all(cls, user=None):
        """
        Get all location (by owner)
        """
        locations = cls.objects
        user = None
        if user:
            locations = locations.filter(owner=user)
        return locations.order_by('label')


class Area(models.Model):
    """Areas: towns, regions, ... mainly set by import"""
    label = models.CharField(max_length=150, verbose_name=_(u"label"))
    polygon = models.PolygonField(_(u"polygon"),
                                  srid=settings.COOP_GEO_EPSG_PROJECTION)
    parent = models.ForeignKey('Area', verbose_name=_(u"parent"), blank=True,
                               null=True)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.label

    def save(self, *args, **kwargs):
        if self.pk and self.parent and self.pk == self.parent.pk:
            raise ValidationError(u"You can't set a parent relative to itself.")
        return super(Area, self).save(*args, **kwargs)

    @property
    def level(self):
        if hasattr(self, '_level') and isinstance(self._level, int):
            return self._level
        level = 0
        if not self.parent or self.parent == self:
            self._level = 0
        else:
            self._level = self.parent.level + 1
        return self._level

    @property
    def leaf(self):
        if not hasattr(self, '_leaf'):
            self._leaf = False
        return self._leaf

    @property
    def end_leaf(self):
        if not hasattr(self, '_end_leaf'):
            self._end_leaf = 0
        return self._end_leaf

    @classmethod
    def get_all(cls):
        """
        Get areas sorted in a tree style
        """
        areas = cls.objects.order_by('-parent', 'label').all()
        sorted_areas = []

        area_childs_dct = {}
        for area in areas:
            if not area.parent:
                continue
            parent_pk = area.parent.pk
            if area.parent.pk not in area_childs_dct:
                area_childs_dct[parent_pk] = []
            area_childs_dct[parent_pk].append(area)

        def _get_childs(area, level):
            level += 1
            if area.pk not in area_childs_dct:
                return
            childs = []
            for child in area_childs_dct[area.pk]:
                child._level = level
                childs.append(child)
                childs_of_child = _get_childs(child, level)
                if childs_of_child:
                    childs[-1]._leaf = True
                    if not hasattr(childs_of_child[-1], '_end_leaf'):
                        childs_of_child[-1]._end_leaf = 0
                    childs_of_child[-1]._end_leaf += 1
                    childs += childs_of_child
            return childs

        for area in areas:
            if area.parent:
                break
            area._level = 0
            sorted_areas.append(area)
            childs = _get_childs(area, 0)
            if childs:
                sorted_areas[-1]._leaf = True
                if not hasattr(childs[-1], '_end_leaf'):
                    childs[-1]._end_leaf = 0
                childs[-1]._end_leaf += 1
                sorted_areas += childs
        return sorted_areas

