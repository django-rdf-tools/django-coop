# -*- coding:utf-8 -*-
from django.contrib import admin
from local.models import Membre,Role,Engagement,Initiative
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from django_extensions.admin.widgets import ForeignKeySearchInput

admin.site.register(Role)


class EngagementInline(admin.TabularInline):
    model = Engagement
    extra=1

class InitiativeAdmin(admin.ModelAdmin):
    list_display = ('title','uri',)
    list_display_links =('title',)
    ordering = ('title',)
    inlines = [
            EngagementInline,
        ]
    
admin.site.register(Initiative, InitiativeAdmin)

class MembreAdmin(admin.ModelAdmin):
    list_display = ('nom','prenom','email',)
    list_display_links =('nom','prenom')
    ordering = ('nom',)
    inlines = [
            EngagementInline,
        ]
 
admin.site.register(Membre, MembreAdmin)



