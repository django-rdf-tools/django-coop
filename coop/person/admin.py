# -*- coding:utf-8 -*-
from django.contrib import admin
from django.conf import settings
from django import forms
from coop.org.admin import create_action, ContactInline, OrgInline
from django.db.models.loading import get_model

from chosen import widgets as chosenwidgets
from coop.utils.autocomplete_admin import FkAutocompleteAdmin


if 'coop.mailing' in settings.INSTALLED_APPS:
    from coop.mailing.admin import SubscribtionMailingListInline


class PersonAdminForm(forms.ModelForm):
    # category = chosenforms.ChosenModelMultipleChoiceField(
    #         required=False,
    #         overlay=_(u"Choose one or more categories"),
    #         queryset=get_model('coop_local', 'PersonCategory').objects.all())

    class Meta:
        widgets = {'category': chosenwidgets.ChosenSelectMultiple(),
                    'sites': chosenwidgets.ChosenSelectMultiple()}

    def __init__(self, *args, **kwargs):
        super(PersonAdminForm, self).__init__(*args, **kwargs)
        self.fields['category'].help_text = None
        self.fields['location'].help_text = None
        if 'sites' in self.fields:
            self.fields['sites'].help_text = None


class PersonAdmin(FkAutocompleteAdmin):
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
    related_search_fields = {'location': ('label', 'adr1', 'adr2', 'zipcode', 'city'), }

    form = PersonAdminForm
    search_fields = ['last_name', 'first_name']
    list_display = ('last_name', 'first_name', 'structure', 'has_user_account', 'has_role')
    list_filter = ('category',)
    list_display_links = ('last_name', 'first_name')
    search_fields = ('last_name', 'first_name', 'structure')
    ordering = ('last_name',)
    inlines = [ContactInline,
                OrgInline,
                ]
    if "coop.mailing" in settings.INSTALLED_APPS:
        inlines.append(SubscribtionMailingListInline)


    def get_actions(self, request):
        myactions = dict(create_action(s) for s in get_model('coop_local', 'PersonCategory').objects.all())
        return dict(myactions, **super(PersonAdmin, self).get_actions(request))  # merging two dicts

    fieldsets = (
        ('Identification', {
            'fields': ['first_name', 'last_name', 'pref_email',
                        ('location', 'location_display'),  # Using coop-geo
                        'category'
                        ],
            }),
        ('Notes', {
            'fields': ('structure', 'notes',)
        })
    )

    if settings.COOP_USE_SITES:
        fieldsets[0][1]['fields'].insert(0, 'sites')


