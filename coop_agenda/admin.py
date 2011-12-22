# -*- coding:utf-8 -*-

from django.contrib import admin
from coop_agenda.models import *
#from genericadmin.admin import GenericAdminModelAdmin
# GenericStackedInline or GenericTabularInline
# on fera le lien generique depuis l'objet en question si besoin (article, événement)

class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('label', 'abbr')

class OccurrenceInline(admin.TabularInline):
    model = Occurrence
    extra = 1

class EventAdmin(admin.ModelAdmin):
    #content_type_blacklist = ('auth/group', 'auth/user', )
    list_display = ('title', 'event_type', 'description')
    list_filter = ('event_type', )
    search_fields = ('title', 'description')
    inlines = [OccurrenceInline,]

admin.site.register(Event, EventAdmin)
admin.site.register(EventType, EventTypeAdmin)

admin.site.register(Calendar)