# -*- coding:utf-8 -*-
from django.contrib import admin
from coop_local.models import Membre,Role,Engagement,Initiative, Site
from coop_local.forms import SiteForm
from coop.place.admin import BaseSiteAdmin
from coop.admin import BaseEngagementInline,BaseSiteInline,BaseInitiativeAdminForm,BaseInitiativeAdmin,BaseMembreAdmin
from skosxl.models import Term
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from coop.autocomplete_admin import FkAutocompleteAdmin,InlineAutocompleteAdmin

admin.site.register(Role)


class EngagementInline(BaseEngagementInline,InlineAutocompleteAdmin):
    model = Engagement

class SiteInline(BaseSiteInline,InlineAutocompleteAdmin):
    model = Site


class InitiativeAdminForm(BaseInitiativeAdminForm):
    class Meta:
        model = Initiative


class InitiativeAdmin(BaseInitiativeAdmin,FkAutocompleteAdmin):
    form = BaseInitiativeAdminForm
    inlines = [
            SiteInline,EngagementInline
        ]
    
admin.site.register(Initiative, InitiativeAdmin)

class MembreAdmin(BaseMembreAdmin):
    inlines = [
            EngagementInline,
        ]

admin.site.register(Membre, MembreAdmin)

class SiteAdmin(BaseSiteAdmin):
     form = SiteForm

admin.site.register(Site, SiteAdmin)


