# -*- coding:utf-8 -*-
from django import forms
from django.contrib import admin
from coop.utils.autocomplete_admin import FkAutocompleteAdmin, InlineAutocompleteAdmin, NoLookupsFkAutocompleteAdmin
from django.contrib.contenttypes.generic import GenericTabularInline
from django.utils.translation import ugettext_lazy as _
from django.db.models.loading import get_model



class SimpleLinkForm(forms.ModelForm):
    class Meta:
    	model = get_model('coop_local','Link')
        fields = ['object_uri', 'object_label']


class LinksInline(GenericTabularInline):
    model = get_model('coop_local','Link')
    form = SimpleLinkForm
    verbose_name = _(u'link')
    verbose_name_plural = _(u'links')
    extra = 1

