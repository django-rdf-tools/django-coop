# -*- coding:utf-8 -*-
from django.contrib import admin
from django import forms
from django.conf import settings
from django.db.models.loading import get_model
from django.utils.translation import ugettext_lazy as _
from coop.utils.autocomplete_admin import FkAutocompleteAdmin, InlineAutocompleteAdmin
from coop_local.models import Contact, Person, Location
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.contrib.admin.widgets import AdminURLFieldWidget
from django.db.models import URLField
from django.utils.safestring import mark_safe
from sorl.thumbnail.admin import AdminImageMixin
from tinymce.widgets import AdminTinyMCE
from coop.agenda.admin import DatedInline
from chosen import widgets as chosenwidgets


if "coop_geo" in settings.INSTALLED_APPS:
    from coop_geo.admin import LocatedInline


class ProjectMemberInline(InlineAutocompleteAdmin):
    model = get_model('coop_local', 'ProjectMember')
    verbose_name = _(u'Member')
    verbose_name_plural = _(u'Members')
    fields = ('person', 'role_detail', 'is_contact', 'membership_display')

    related_search_fields = {'person': ('last_name', 'first_name',
                                        'email', 'structure', 'username'), }
    extra = 2


class ProjectSupportInline(InlineAutocompleteAdmin):
    model = get_model('coop_local', 'ProjectSupport')
    verbose_name = _(u'Project partner')
    verbose_name_plural = _(u'Project partners')
    fk_name = 'project'
    fields = ('relation_type', 'partner')
    related_search_fields = {'partner': ('title', 'subtitle', 'acronym',), }
    extra = 1


class ProjectAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectAdminForm, self).__init__(*args, **kwargs)
        if 'sites' in self.fields:
            self.fields['sites'].help_text = None
        self.fields['category'].help_text = None

    class Meta:
        widgets = {'sites': chosenwidgets.ChosenSelectMultiple(),
                    'category': chosenwidgets.ChosenSelectMultiple()}


class ProjectAdmin(FkAutocompleteAdmin):
    form = ProjectAdminForm
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
    list_display = ('title', 'organization', 'zone')
    list_filter = ['status']
    fieldsets = (
       ('Description', {
            'fields': ['title', 'status', 'start', 'end', 'description', 
                        'organization', 'published', 'zone', 'budget', 'notes',
                        'category', 'tags']
        }),

    )
    related_search_fields = {'organization': ('title', 'subtitle', 'acronym',),
                             'zone': ('label', 'reference')}
    inlines = [ProjectSupportInline,
               ProjectMemberInline,
               LocatedInline,
               DatedInline
               ]

    if settings.COOP_USE_SITES:
        fieldsets[0][1]['fields'].insert(0, 'sites')
        list_filter.append('sites')


