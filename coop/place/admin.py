#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from django.contrib import admin

from coop.place.forms import BaseSiteForm
from coop_geo import widgets

class BaseSiteAdmin(admin.ModelAdmin):
    list_display = ('adr1', 'adr2', 'zipcode', 'city')
    ordering = ('title',)
    form = BaseSiteForm

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name != 'location':
            return super(BaseSiteAdmin, self).formfield_for_dbfield(db_field,
                                                                    **kwargs)
        if db_field.__class__ in self.formfield_overrides:
            kwargs = dict(self.formfield_overrides[db_field.__class__], **kwargs)

        # Get the correct formfield.
        if isinstance(db_field, models.ForeignKey):
            formfield = self.formfield_for_foreignkey(db_field, **kwargs)
        elif isinstance(db_field, models.ManyToManyField):
            formfield = self.formfield_for_manytomany(db_field, **kwargs)
        formfield.widget = widgets.ChooseLocationWidget(kwargs['request'].user)
        return formfield

