# -*- coding:utf-8 -*-
from django.contrib import admin
from coop_local.models import MailingList

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

admin.site.register(MailingList)
