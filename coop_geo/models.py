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
    point = models.PointField(_(u"point"), blank=True, null=True,
                              srid=settings.COOP_GEO_EPSG_PROJECTION)
    area = models.ForeignKey('Area', verbose_name=_(u'area'), blank=True,
                              null=True)
    owner = models.ForeignKey(User, verbose_name=_(u'owner'), blank=True,
                              null=True)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.label

    def save(self, *args, **kwargs):
        if not self.point and not self.area:
            raise ValidationError(u"You must at least set a point or choose "
                                  u"an area.")
        return super(Location, self).save(*args, **kwargs)

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

#TODO: manage relations
#TODO: manage auto parent area

AREA_DEFAULT_LOCATION_LBL = _(u"%s (center)")

class Area(models.Model):
    """Areas: towns, regions, ... mainly set by import"""
    label = models.CharField(max_length=150, verbose_name=_(u"label"))
    reference = models.CharField(max_length=150, verbose_name=_(u"reference"),
                                 blank=True, null=True)
    polygon = models.PolygonField(_(u"polygon"),
                                  srid=settings.COOP_GEO_EPSG_PROJECTION)
    default_location = models.ForeignKey(Location, blank=True, null=True,
            verbose_name=_(u"default location"), related_name='associated_area')
    related_areas = models.ManyToManyField('Area',
            verbose_name=_(u"related area"), through='AreaRelations')
    # when set to true a "parent" area is automaticaly updated with the add
    # of new childs
    update_auto = models.BooleanField(verbose_name=_(u"update automatically?"),
                                      default=False)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.label

    def save(self, *args, **kwargs):
        if not self.default_location:
            datas = {'point':self.polygon.centroid,
                     'label':AREA_DEFAULT_LOCATION_LBL % self.label}
            self.default_location = Location.objects.create(**datas)
        returned = super(Area, self).save(*args, **kwargs)
        if self.parent_rels.count():
            for parentrel in self.parent_rels.all():
                print "YO"*10
                parentrel.parent.update_from_childs()
        return returned

    def add_parent(self, parent, relation_type):
        if parent == self:
            raise ValidationError(u"You can't set a parent relative to itself.")
        self.related_areas.through.objects.create(child=self, parent=parent,
                                          relation_type=relation_type)

    def add_child(self, child, relation_type):
        if child == self:
            raise ValidationError(u"You can't set a parent relative to itself.")
        self.related_areas.through.objects.create(child=child, parent=self,
                                                  relation_type=relation_type)

    def update_from_childs(self):
        if not self.update_auto or not self.child_rels.count():
            return
        geocollection = [childrel.child.polygon
                         for childrel in self.child_rels.all()]
        self.polygon = geocollection[0]
        for polygon in geocollection[1:]:
            self.polygon = self.polygon.union(polygon)
        self.save()
        return

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

RELATION_TYPES = (('RG', u'région'),
                  ('DP', u"département"),
                  ('CC', u"communauté de commune"),
                  )

class AreaRelations(models.Model):
    """
    Relations between areas.
    """
    relation_type = models.CharField(max_length=2, verbose_name=_(u"type"),
                                     choices=RELATION_TYPES)
    parent = models.ForeignKey(Area, related_name='child_rels')
    child = models.ForeignKey(Area, related_name='parent_rels')

    def save(self, *args, **kwargs):
        super(AreaRelations, self).save(*args, **kwargs)
        self.parent.update_from_childs()
