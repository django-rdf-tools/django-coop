# -*- coding:utf-8 -*-

from django.conf import settings
from django.contrib import admin
from django import forms
from coop_local.models import Event, EventCategory, Calendar, Occurrence, Dated
from coop.utils.autocomplete_admin import FkAutocompleteAdmin, InlineAutocompleteAdmin, NoLookupsFkAutocompleteAdmin
from coop_geo.admin import LocatedInline
from django.contrib.contenttypes.generic import GenericTabularInline
from django.utils.translation import ugettext_lazy as _
from coop.agenda.forms import SingleOccurrenceForm
from django.db.models.loading import get_model
from chosen import widgets as chosenwidgets
from coop.doc.admin import AttachmentsInline
from coop.link.admin import LinksInline

#from genericadmin.admin import GenericAdminModelAdmin
# GenericStackedInline or GenericTabularInline
# on fera le lien generique depuis l'objet en question si besoin (article, événement)


class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('label',)


class OccurrenceInline(admin.StackedInline):
    #form = SingleOccurrenceForm
    verbose_name = _(u'Date')
    verbose_name_plural = _(u'Dates')
    model = get_model('coop_local', 'Occurrence')
    extra = 1


class EventAdminForm(forms.ModelForm):
    class Meta:
        model = get_model('coop_local', 'Event')
        widgets = {'sites': chosenwidgets.ChosenSelectMultiple(),
                   'category': chosenwidgets.ChosenSelectMultiple()
                   }

    def __init__(self, *args, **kwargs):
        # initial = {
        #     'category': 1, 
        #     'calendar': 1 
        #     }
        # if not kwargs.has_key('initial'):
        # #     kwargs['initial'].update(initial)
        # # else:
        #     kwargs['initial'] = initial
        # Initializing form only after you have set initial dict
        super(EventAdminForm, self).__init__(*args, **kwargs)
        self.fields['calendar'].initial = Calendar.objects.get(id=1)
        self.fields['category'].help_text = None
        # self.fields['category'].initial = EventCategory.objects.get(id=1)
        if 'sites' in self.fields:
            self.fields['sites'].help_text = None


class EventAdmin(NoLookupsFkAutocompleteAdmin):
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
    form = EventAdminForm
    list_display = ('title', 'description', 'active')
    list_filter = ('category', 'active')
    search_fields = ('title', 'description')
    related_search_fields = {'person': ('last_name', 'first_name',
                                        'email', 'structure', 'username'),
                            'organization': ('title', 'acronym', 'subtitle', 'description'),
                            'location': ('label', 'adr1', 'adr2', 'zipcode', 'city'),
    }
    fieldsets = [['Description', {'fields': ['title', 'description',
        'category', ('calendar', 'active'),
        'organization', 'remote_organization_label', 'remote_organization_uri',
        'person', 'remote_person_label', 'remote_person_uri',
        'location', 'remote_location_label', 'remote_location_uri',
      ]}],
    ]

    if "coop_tag" in settings.INSTALLED_APPS:
        fieldsets[0][1]['fields'].insert(2, 'tags')

    if settings.COOP_USE_SITES:
        fieldsets[0][1]['fields'].insert(0, 'sites')

    inlines = [OccurrenceInline, AttachmentsInline, LinksInline]


class DatedInline(GenericTabularInline, InlineAutocompleteAdmin):
    verbose_name = _(u'Date')
    verbose_name_plural = _(u'Dates')
    model = get_model('coop_local', 'Dated')
    related_search_fields = {'event': ('title', 'description', 'slug'), }
    extra = 1


from coop_geo.models import AreaType
from coop_local.models import Area

class GenericDateInlineForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(GenericDateInlineForm, self).__init__(*args, **kwargs)
        commune = AreaType.objects.get(txt_idx="COM")
        pays = AreaType.objects.get(txt_idx="COUNTRY")
        self.fields['commune_fr'].queryset = Area.objects.filter(area_type=commune)
        self.fields['pays'].queryset = Area.objects.filter(area_type=pays)


class GenericDateInline(GenericTabularInline, InlineAutocompleteAdmin):
    verbose_name = _(u'Date')
    verbose_name_plural = _(u'Dates')
    model = get_model('coop_local', 'GenericDate')
    extra = 1
    related_search_fields = {'commune_fr': ('label',),
                             'pays': ('label',),
                             }

    class Meta:
        form = GenericDateInlineForm

