# -*- coding:utf-8 -*-
from django.contrib import admin
from django import forms
from coop.exchange.models import BaseExchange, BasePaymentModality, BaseTransaction, BaseProduct

from django.db.models.loading import get_model
from django.utils.translation import ugettext_lazy as _
from coop.utils.autocomplete_admin import FkAutocompleteAdmin, InlineAutocompleteAdmin
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from coop_geo.admin import LocatedInline
from tinymce.widgets import AdminTinyMCE


class PaymentInline(admin.TabularInline):
    model = get_model('coop_local', 'PaymentModality')
    #model = BasePaymentModality
    extra = 0


class ExchangeForm(forms.ModelForm):
    description = forms.CharField(widget=AdminTinyMCE(attrs={'cols': 80, 'rows': 60}))

    class Meta:
        model = get_model('coop_local', 'Exchange')


class ExchangeInline(admin.StackedInline):
    form = ExchangeForm
    model = get_model('coop_local', 'Exchange')
    # verbose_name = _(u'Exchange')
    # verbose_name_plural = _(u'Exchanges')
    #form = ExchangeInlineLinkForm 
    # needed to include a link to the change_form / only because nested inlines are not possible
    fieldsets = ((None, {'fields': ('etype', 'title',  # 'permanent','expiration'
                                    'description', 'tags')}),)  # If you site uses coop-tag

    extra = 1
    #class Media: js = ('js/expiration.js',)


class BaseProductInline(admin.StackedInline):
    model = BaseProduct
    fieldsets = ((None, {'fields': ('title',
                                    'description',
                                    )}),)
    extra = 1


class BaseTransactionInline(admin.StackedInline):
    model = BaseTransaction
    fk_name = 'destination_org'
    fieldsets = ((None, {'fields': ('title', 'origin', 'description')}),)
    #related_search_fields = {'origin': ('title', 'description', 'organization__title'), }
    extra = 1


class BaseExchangeAdmin(ForeignKeyAutocompleteAdmin):  # AdminImageMixin,
    fieldsets = ((None, {
            'fields': (('etype', 'permanent', 'expiration', ), 'title', 'description',
                       'organization'
                       )
            }),)
    related_search_fields = {'organization': ('title', 'subtitle', 'description'), }
    inlines = [
            PaymentInline,
            LocatedInline,  # Using coop-geo
        ]


