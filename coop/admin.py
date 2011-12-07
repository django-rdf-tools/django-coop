# -*- coding:utf-8 -*-
from django.contrib import admin
from coop.membre.models import BaseMembre
from coop.initiative.models import BaseRole,BaseEngagement,BaseInitiative
from coop.place.models import BaseSite
from skosxl.models import Term
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from coop.autocomplete_admin import FkAutocompleteAdmin,InlineAutocompleteAdmin


class BaseEngagementInline(InlineAutocompleteAdmin):
    model = BaseEngagement
    related_search_fields = {'membre': ('nom','prenom','email','user__username'), }
    extra=1

class BaseSiteInline(admin.StackedInline,InlineAutocompleteAdmin):
    model = BaseSite
    related_search_fields = {'location': ('label','adr1','adr2','zipcode','city'), }
    extra=0

class BaseInitiativeAdminForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Term.objects.all().order_by('literal'),
        widget=FilteredSelectMultiple('tags', False)
    )
    class Meta:
        model = BaseInitiative

class BaseInitiativeAdmin(FkAutocompleteAdmin):
    form = BaseInitiativeAdminForm
    list_display = ('title','active','uri')
    list_display_links =('title',)
    search_fields = ['title','acronym','description']
    list_filter = ('active',)
    ordering = ('title',)
    inlines = [
            BaseSiteInline,BaseEngagementInline
        ]
    
class BaseMembreAdmin(admin.ModelAdmin):
    list_display = ('nom','prenom','email',)
    list_display_links =('nom','prenom')
    ordering = ('nom',)
    inlines = [
            BaseEngagementInline,
        ]


