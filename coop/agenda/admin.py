# -*- coding:utf-8 -*-

from django.conf import settings
from django.contrib import admin
from coop_local.models import Event, EventCategory, Calendar, Occurrence
from coop.utils.autocomplete_admin import FkAutocompleteAdmin, InlineAutocompleteAdmin

#from genericadmin.admin import GenericAdminModelAdmin
# GenericStackedInline or GenericTabularInline
# on fera le lien generique depuis l'objet en question si besoin (article, événement)


class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('label',)


class OccurrenceInline(admin.TabularInline):
    model = Occurrence
    extra = 1


class EventAdmin(FkAutocompleteAdmin):
    #content_type_blacklist = ('auth/group', 'auth/user', )
    list_display = ('title', 'event_type', 'description')
    list_filter = ('event_type', )
    search_fields = ('title', 'description')
    related_search_fields = {'person': ('last_name', 'first_name',
                                        'email', 'structure', 'username'),
                            'organization': ('title', 'acronym', 'subtitle', 'description')
    }
    fieldsets = [[None, {'fields': ['title', 'description',
        ('event_type', 'calendar'),
        ('organization', 'person'),
        #'remote_organization_label'
      ]}],
    ]

    if "coop.agenda" in settings.INSTALLED_APPS:
        fieldsets[0][1]['fields'].insert(2, 'tags')

    inlines = [OccurrenceInline, ]

admin.site.register(Event, EventAdmin)
admin.site.register(EventCategory, EventCategoryAdmin)
admin.site.register(Calendar)
