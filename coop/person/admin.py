# -*- coding:utf-8 -*-
from django.contrib import admin
from django import forms
from coop.org.admin import create_action, ContactInline, OrgInline
from django.db.models.loading import get_model

from chosen import widgets as chosenwidgets
from django_extensions.admin import ForeignKeyAutocompleteAdmin


class PersonAdminForm(forms.ModelForm):
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html' 
    # category = chosenforms.ChosenModelMultipleChoiceField(
    #         required=False,
    #         overlay=_(u"Choose one or more categories"),
    #         queryset=get_model('coop_local', 'PersonCategory').objects.all())  

    class Meta:
        widgets = {'category': chosenwidgets.ChosenSelectMultiple()}


class PersonAdmin(ForeignKeyAutocompleteAdmin):  # FkAutocompleteAdmin too but...
    form = PersonAdminForm
    search_fields = ['last_name', 'first_name', 'email']
    list_display = ('last_name', 'first_name', 'email', 'structure', 'has_user_account', 'has_role')
    list_filter = ('category',)
    list_display_links = ('last_name', 'first_name')
    search_fields = ('last_name', 'first_name', 'email', 'structure')    
    ordering = ('last_name',)
    inlines = [
                ContactInline,
                OrgInline,
                ]

    def get_actions(self, request):
        myactions = dict(create_action(s) for s in get_model('coop_local', 'PersonCategory').objects.all())
        return dict(myactions, **super(PersonAdmin, self).get_actions(request))  # merging two dicts
    
    fieldsets = (
        (None, {
            'fields': (('first_name', 'last_name'),
                        'email',
                        'category'
                        ),
            }),
        ('Notes', {
            'classes': ('collapse',),
            'fields': ('structure', 'notes',)
        })
    )

