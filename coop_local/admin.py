# -*- coding:utf-8 -*-
from django.contrib import admin
from coop_local.models import Membre,Role,Engagement,Initiative, Site, SeeAlsoLink, SameAsLink
from coop_local.forms import SiteForm
from coop.place.admin import BaseSiteAdmin
from coop.admin import BaseEngagementInline,BaseSiteInline,BaseInitiativeAdminForm,BaseInitiativeAdmin,BaseMembreAdmin
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from coop.autocomplete_admin import FkAutocompleteAdmin,InlineAutocompleteAdmin

admin.site.register(Role)


from genericadmin.admin import GenericAdminModelAdmin,GenericTabularInline
#GenericStackedInline or 

class SeeAlsoInline(GenericTabularInline):
    model = SeeAlsoLink
    extra=1
    
class SameAsInline(GenericTabularInline):
    model = SameAsLink
    extra=1    

class EngagementInline(BaseEngagementInline,InlineAutocompleteAdmin):
    model = Engagement

class SiteInline(BaseSiteInline,InlineAutocompleteAdmin):
    model = Site


class InitiativeAdminForm(BaseInitiativeAdminForm):
    class Meta:
        model = Initiative


class InitiativeAdmin(BaseInitiativeAdmin,FkAutocompleteAdmin,GenericAdminModelAdmin):
    form = BaseInitiativeAdminForm
    inlines = [
            SiteInline,EngagementInline,SeeAlsoInline
        ]
    
admin.site.register(Initiative, InitiativeAdmin)

class MembreAdmin(BaseMembreAdmin,GenericAdminModelAdmin):
    inlines = [
            EngagementInline,SeeAlsoInline,SameAsInline
        ]

admin.site.register(Membre, MembreAdmin)

class SiteAdmin(BaseSiteAdmin):
     form = SiteForm

admin.site.register(Site, SiteAdmin)


