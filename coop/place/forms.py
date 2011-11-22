#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import forms
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
#import floppyforms as forms

from coop_geo import widgets

from models import BaseSite


class BaseSiteForm(forms.ModelForm):
    class Meta:
        model = BaseSite
        fields = ('title', 'description', 'site_principal', 'location',
                  'adr1', 'adr2', 'zipcode', 'city',)



