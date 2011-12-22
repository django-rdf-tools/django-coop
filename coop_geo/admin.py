#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

import models
import forms

class LocationAdmin(admin.ModelAdmin):
    list_display = ['label', 'adr1', 'adr2', 'zipcode', 'city']
    form = forms.LocationForm
admin.site.register(models.Location, LocationAdmin)

class AreaAdmin(admin.ModelAdmin):
    list_display = ['label', 'reference', 'area_type',]
    list_filter = ['area_type',]
    model = models.Area
    form = forms.AreaForm
admin.site.register(models.Area, AreaAdmin)

class AreaRelAdmin(admin.ModelAdmin):
    list_display = ['parent', 'child', 'relation_type',]
    list_filter = ['relation_type',]
    model = models.AreaRelations
    form = forms.AreaRelationsForm
admin.site.register(models.AreaRelations, AreaRelAdmin)

