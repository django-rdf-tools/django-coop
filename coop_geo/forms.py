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
        fields = ('label', 'point', 'polygon')
        widgets = {
            'label': forms.TextInput(),
            'point': widgets.PointWidget(),
        }

    def clean(self):
        cleaned_data = self.cleaned_data
        if not cleaned_data.get('point') and not cleaned_data.get('polygon'):
            raise ValidationError(u"You must set a point or a polygon.")
        return cleaned_data

