# -*- coding:utf-8 -*-
from django.contrib import admin
from django import forms
from coop.exchange.models import BaseTransaction, BaseProduct
from django.db.models.loading import get_model
from django.utils.translation import ugettext_lazy as _
from coop.utils.autocomplete_admin import FkAutocompleteAdmin, InlineAutocompleteAdmin, NoLookupsFkAutocompleteAdmin
from coop_geo.admin import LocatedInline
from tinymce.widgets import AdminTinyMCE
from coop.utils.fields import MultiSelectFormField, MethodsCheckboxSelectMultiple, DomainCheckboxSelectMultiple
from coop.exchange.models import ETYPE
from django.conf import settings
from chosen import widgets as chosenwidgets
from coop.doc.admin import AttachmentsInline

from coop.admin import ObjEnabledInline

# class PaymentInline(admin.TabularInline):
#     model = get_model('coop_local', 'PaymentModality')
#     #model = BasePaymentModality
#     extra = 0

if 'coop.exchange' in settings.INSTALLED_APPS:

    class ExchangeMethodForm(forms.ModelForm):
        etypes = MultiSelectFormField(widget=DomainCheckboxSelectMultiple(), choices=ETYPE.CHOICES)

        class Meta:
            model = get_model('coop_local', 'ExchangeMethod')

    class ExchangeMethodAdmin(admin.ModelAdmin):  # AdminImageMixin,
        form = ExchangeMethodForm
        list_display = ('label', 'applications')



    class ExchangeAdminForm(forms.ModelForm):
        description = forms.CharField(widget=AdminTinyMCE(attrs={'cols': 80, 'rows': 60}), required=False)
        methods = forms.ModelMultipleChoiceField(   queryset=get_model('coop_local', 'ExchangeMethod').objects.all(),
                                                    widget=MethodsCheckboxSelectMultiple(),
                                                    required=False)

        def __init__(self, *args, **kwargs):
            super(ExchangeAdminForm, self).__init__(*args, **kwargs)
            self.fields['methods'].help_text = ''
            self.fields['methods'].label = _(u'exchange methods')
            if 'tags' in self.fields:
                self.fields['tags'].label = 'Tags'
            if 'sites' in self.fields:
                self.fields['sites'].help_text = None

        class Media:
            js = ('js/select_exchange_methods.js',)

        class Meta:
            model = get_model('coop_local', 'Exchange')
            widgets = {'sites': chosenwidgets.ChosenSelectMultiple()}


    class ExchangeAdmin(NoLookupsFkAutocompleteAdmin):  # AdminImageMixin,
        form = ExchangeAdminForm
        change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
        list_display = ('title', 'organization', 'newsletter')
        list_editable = ['newsletter']
        fieldsets = (('Description', {'fields': [('eway', 'etype'),
                                         'methods',
                                         'title',
                                         'description', 'tags',
                                        'organization', 'remote_organization_label', 'remote_organization_uri',
                                        'person', 'remote_person_label', 'remote_person_uri',
                                         'newsletter',]
                            }),)
        inlines = [AttachmentsInline,]
        related_search_fields = {'person': ('last_name', 'first_name',
                                            'email', 'structure', 'username'),
                                 'organization': ('title', 'acronym', 'subtitle', 'description'),
                                 }
        if settings.COOP_USE_SITES:
            fieldsets[0][1]['fields'].insert(0, 'sites')




    class ExchangeInline(admin.StackedInline, ObjEnabledInline):
        form = ExchangeAdminForm
        model = get_model('coop_local', 'Exchange')
        fieldsets = ((None, {'fields': (('eway', 'etype'),
                                         'methods',
                                         'title',
                                        'description',  # 'tags',
                                        'location', 'area',)
                            }),)
        extra = 1

        def formfield_for_dbfield(self, db_field, **kwargs):
            if self.parent_obj != None:
                if db_field.name == 'location':
                    kwargs['queryset'] = self.parent_obj.locations()  # default : only org's locations
                if db_field.name == 'area':
                    kwargs['queryset'] = self.parent_obj.areas()  # default : only org's areas
                if db_field.name == 'person':
                    kwargs['queryset'] = self.parent_obj.members.all()  # default : only org's members
            return super(ExchangeInline, self).formfield_for_dbfield(db_field, **kwargs)

    class ProductInline(admin.StackedInline):
        model = BaseProduct
        fieldsets = ((None, {'fields': ('title',
                                        'description',
                                        )}),)
        extra = 1

    class TransactionInline(admin.StackedInline):
        model = BaseTransaction
        fk_name = 'destination_org'
        fieldsets = ((None, {'fields': ('title', 'origin', 'description')}),)
        #related_search_fields = {'origin': ('title', 'description', 'organization__title'), }
        extra = 1



