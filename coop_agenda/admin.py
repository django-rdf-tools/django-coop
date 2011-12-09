from django.contrib import admin
from coop_agenda.models import *
from genericadmin.admin import GenericAdminModelAdmin
#GenericStackedInline or GenericTabularInline

class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('label', 'abbr')

class OccurrenceInline(admin.TabularInline):
    model = Occurrence
    extra = 1

class EventAdmin(GenericAdminModelAdmin):
    list_display = ('title', 'event_type', 'description')
    list_filter = ('event_type', )
    search_fields = ('title', 'description')
    inlines = [OccurrenceInline,]

admin.site.register(Event, EventAdmin)
admin.site.register(EventType, EventTypeAdmin)

admin.site.register(Calendar)