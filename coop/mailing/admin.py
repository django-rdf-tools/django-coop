# -*- coding:utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from coop_local.models import NewsletterSending
from django.db.models.loading import get_model
from coop.utils.autocomplete_admin import FkAutocompleteAdmin
from django.contrib.contenttypes.generic import GenericTabularInline
from coop.mailing.models import instance_to_pref_email
from django import forms
from coop.mailing.soap import exists, sympa_available
from django.contrib.sites.models import Site


from genericadmin.admin import GenericAdminModelAdmin, GenericTabularInline


class SubscriptionInline(GenericTabularInline):
    model = get_model('coop_local', 'Subscription')
    # fk_name = 'mailing_list'
    verbose_name = _(u'subscription')
    verbose_name_plural = _(u'subscriptions')
    content_type_whitelist = ('coop_local/person', 'coop_local/organization')
    extra = 1


class MailingListInline(admin.TabularInline):
    model = get_model('coop_local', 'MailingList')
    verbose_name = _(u'mailing list')
    verbose_name_plural = _(u'mailing list')
    fields = ('name', 'subject', 'description')
    readonly_fields = ('email',)
    extra = 1


# On ne peut pas heriter de ObjEnabledInline le polymorphisme ne passe pas 
# Car GenericTabularInline surcharge aussi la method get_formset
# class SubscribtionMailingListInline(GenericTabularInline):
#     model = get_model('coop_local', 'Subscription')
#     verbose_name = _(u'subscription')
#     verbose_name_plural = _(u'subscriptions')
#     fields = ('mailing_list', 'label', 'email')  
#     # inlines = [MailingListInline, ]  Ne s'écrit pas comme cela
#     related_search_fields = {'email': ('last_name', 'first_name',
#                                         'email', 'structure', 'username'), }

#     extra = 1

#     def get_formset(self, request, obj=None, **kwargs):
#         # Hack! Hook parent obj just in time to use in formfield_for_manytomany
#         self.parent_obj = obj
#         return super(SubscribtionMailingListInline, self).get_formset(
#             request, obj, **kwargs)

#     def formfield_for_dbfield(self, db_field, **kwargs):
#         if self.parent_obj != None:
#             if db_field.name == 'label':
#                 kwargs['initial'] = self.parent_obj.label()
#             if db_field.name == 'email':
#                 kwargs['initial'] = instance_to_pref_email(self.parent_obj)
#         return super(SubscribtionMailingListInline, self).formfield_for_dbfield(db_field, **kwargs)




class MailingListAdminForm(forms.ModelForm):
    # Non : il faut pouvoir modifier la list... comment modifier son template et sa description???
    # def clean_name(self):
    #     import pdb
    #     pdb.set_trace()
    #     name = self.cleaned_data['name']
    #     if exists(name):
    #         raise forms.ValidationError(u"La liste %s existe déjà" % name)
    #     return name

    def clean_description(self):
        desc = self.cleaned_data['description']
        if desc == '':
            return self.data['name']
        else:
            return desc

    class Meta:
        model = get_model('coop_local', 'MailingList')


class MailingListAdmin(GenericAdminModelAdmin, FkAutocompleteAdmin):
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
    # list_display_links = ['email', ]
    form = MailingListAdminForm
    search_fields = ['name', 'subject', 'email', 'description']
    list_per_page = 10
    list_select_related = True
    read_only_fields = ['created', 'modified']
    ordering = ('name',)
    readonly_fields = ('email',)

    inlines = [SubscriptionInline]

    fieldsets = (
        ('Description', {
            'fields': ['name',
                       'subject', 
                       'description', 
                       'email',
                        ('subscription_option', 'subscription_filter_with_tags'),
                        'person_category', 'organization_category',
                       'tags'
                       ]
            }),
    )




class NewsletterSendingInline(admin.StackedInline):
    #form = SingleOccurrenceForm
    verbose_name = _(u'Sending Date')
    verbose_name_plural = _(u'Sending Dates')
    model = NewsletterSending
    extra = 1


class NewsletterAdmin(admin.ModelAdmin):
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
    inlines = [NewsletterSendingInline]

