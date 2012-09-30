from django.contrib import admin

from preferences.admin import PreferencesAdmin
from coop_local.models import SitePrefs
from coop.utils.autocomplete_admin import FkAutocompleteAdmin, InlineAutocompleteAdmin


class SitePrefsAdmin(PreferencesAdmin, FkAutocompleteAdmin):
    related_search_fields = {'main_organization': ('title', 'subtitle', 'acronym'), }

admin.site.register(SitePrefs, SitePrefsAdmin)
