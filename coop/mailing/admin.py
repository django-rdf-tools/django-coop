# -*- coding:utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from coop_local.models import Newsletter, Subscription
from django.db.models.loading import get_model
from coop.utils.autocomplete_admin import FkAutocompleteAdmin
from django.contrib.contenttypes.generic import GenericTabularInline

# from django.conf import settings
# from django.utils.translation import ugettext_lazy as _
# from django.contrib import admin, messages
# from coop.mailing.forms import MailingListAdminForm
# from coop_local.models import MailingList
# # from coop.mailing.models import Parameter
# from coop.mailing import soap 



# class ParameterInline(admin.StackedInline):
#     model = Parameter


# class MailingListAdmin(admin.ModelAdmin):
#     form = MailingListAdminForm
#     # fields = ['name', 'subject', 'template', 'description', 'topics']
#     # inlines = [
#     #     ParameterInline,
#     # ]

#     # def save_formset(self, request, form, formset, change):
#     #     import pdb
#     #     pdb.set_trace()
#     #     if not change:
#     #         obj = form.save(commit=False)
#     #         if obj.template == 8 :
#     #             subject = '%s%shttp://%s/sympa_remote_list/%s' % (obj.subject, settings.SYMPA_SOAP['PARAMETER_SEPARATOR'],Site.objects.get_current(), obj.name)
#     #         else:
#     #             subject = obj.subject
#     #         subject = len(formset.cleaned_data) > 0 and '%s%s%s' % (obj.subject, settings.SYMPA_SOAP['PARAMETER_SEPARATOR'], settings.SYMPA_SOAP['PARAMETER_SEPARATOR'].join([data['value'] for data in formset.cleaned_data if data.has_key('value')])) or obj.subject
#     #         result = soap.create_list(obj.name, subject, obj.templateName, obj.description)
#     #         if result == 1:
#     #             obj.save()
#     #             formset.save()
#     #         else:
#     #             obj.delete()
#     #             messages.error(request, _(u"Cannot add the list : %s" % result))


#     def delete_model(self, request, obj):
#         result = 1
#         if soap.exists(obj.name):
#             result = soap.close_list(obj.name)

#         if result == 1 or result == 'list allready closed':
#             obj.delete()
#         else:
#             messages.error(request, _(u"Cannot close the list : %s" % result))


admin.site.register(Newsletter)
admin.site.register(Subscription)


class SubscriptionInline(admin.TabularInline):
    model = get_model('coop_local', 'Subscription')
    # fk_name = 'mailing_list'
    verbose_name = _(u'subscription')
    verbose_name_plural = _(u'subscriptions')
    fields = ('label', 'email')
    extra = 1



class MailingListInline(admin.TabularInline):
    model = get_model('coop_local', 'MailingList')
    verbose_name = _(u'mailing list')
    verbose_name_plural = _(u'mailing list')
    fields = ('name', 'subject', 'description')
    extra = 1


class SubscribtionMailingListInline(GenericTabularInline):
    model = get_model('coop_local', 'Subscription')
    verbose_name = _(u'subscription')
    verbose_name_plural = _(u'subscriptions')
    fields = ('mailing_list', 'label', 'email') # TODO les 2 derniersdoivent avoir une valeur par default
    # inlines = [MailingListInline, ]  Ne s'écrit pas comme cela
    related_search_fields = {'email': ('last_name', 'first_name',
                                        'email', 'structure', 'username'), }

    extra = 1





class MailingListAdmin(FkAutocompleteAdmin):
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
    # list_display_links = ['email', ]
    search_fields = ['name', 'subject', 'email', 'description']
    list_per_page = 10
    list_select_related = True
    read_only_fields = ['created', 'modified']
    ordering = ('name',)

    inlines = [SubscriptionInline]

    fieldsets = (
        ('Description', {
            'fields': ['name', 'subject', 'description', 'subscription_option', 'tags'
                       ]
            }),
    )

