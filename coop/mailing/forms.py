# -*- coding: utf-8 -*-
# from django import forms
# from coop_local.models import MailingList
# from coop.mailing import soap


# class MailingListAdminForm(forms.ModelForm):
    
#     def clean_name(self):
#         name = self.cleaned_data['name']
#         if soap.exists(name):
#             raise forms.ValidationError(u"La liste %s existe déjà" % name)
#         return self.cleaned_data['name']

#     class Meta:
#         model = MailingList
