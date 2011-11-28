#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

import floppyforms as forms
import models
import widgets

class LocationForm(forms.ModelForm):
    class Meta:
        model = models.Location
        fields = ('label', 'point', 'area')
        widgets = {
            'label': forms.TextInput(),
            'point': widgets.PointWidget(),
            'area': forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = self.cleaned_data
        if not cleaned_data.get('point') and not cleaned_data.get('area'):
            raise ValidationError(u"You must at least set a point or choose "
                                  u"an area.")
        return cleaned_data

class AreaForm(forms.ModelForm):
    class Meta:
        model = models.Area
        fields = ('label', 'polygon',)
        widgets = {
            'label': forms.TextInput(),
            'polygon': widgets.PolygonWidget(),
        }

    def clean_parent(self):
        cleaned_data = self.cleaned_data
        parent = cleaned_data.get('parent')
        if parent and self.instance == parent:
            raise ValidationError(u"You can't set a parent relative to itself.")
        return parent

