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
    model = models.Area
    form = forms.AreaForm
admin.site.register(models.Area, AreaAdmin)

class AreaRelAdmin(admin.ModelAdmin):
    model = models.AreaRelations
admin.site.register(models.AreaRelations, AreaRelAdmin)

