# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _
from django.conf import settings
from django import forms
from coop_local.models import Newsletter, NewsletterSending
from django.utils.importlib import import_module
from django.core.exceptions import ValidationError
import floppyforms
from datetime import datetime
from djaloha.widgets import AlohaInput

# from coop.mailing import soap


# class MailingListAdminForm(forms.ModelForm):
    
#     def clean_name(self):
#         name = self.cleaned_data['name']
#         if soap.exists(name):
#             raise forms.ValidationError(u"La liste %s existe déjà" % name)
#         return self.cleaned_data['name']

#     class Meta:
#         model = MailingList


def get_newsletter_templates(newsletter, user=None):
    try:
        return getattr(settings, 'COOP_NEWSLETTERS_TEMPLATES')
    except AttributeError:
        # use default value only
        return [(Newsletter._meta.get_field_by_name('template')[0].default, 'standard')]


def get_newsletter_form():
    try:
        full_class_name = getattr(settings, 'COOP_NEWSLETTER_FORM')
    except AttributeError:
        from coop.mailing.forms import NewsletterForm
        newsletter_form = NewsletterForm
    else:
        module_name, class_name = full_class_name.rsplit('.', 1)
        module = import_module(module_name)
        newsletter_form = getattr(module, class_name)
    return newsletter_form


class NewNewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ('subject', 'template')  #, 'items')
        #widgets = {}
        #try:
        #    widgets.update({
        #        'items': ChosenSelectMultiple(),
        #    })
        #except NameError:
        #    print 'NO ChosenSelectMultiple'
        #    pass

    def __init__(self, user, *args, **kwargs):
        super(NewNewsletterForm, self).__init__(*args, **kwargs)
        tpl_choices = get_newsletter_templates(None, user)
        # if tpl_choices:
        self.fields["template"] = forms.ChoiceField(choices=tpl_choices)
        # else:
        #     self.fields["template"] = forms.CharField()
        self.fields["subject"].widget = forms.TextInput(attrs={'size': 30})


class NewsletterForm(floppyforms.ModelForm):

    class Meta:
        model = Newsletter
        fields = ('subject', 'content',)
        widgets = {
            'subject': AlohaInput(text_color_plugin=False),
            'content': AlohaInput(text_color_plugin=False),
        }

    class Media:
        css = {
            'all': ('css/colorbox.css',),
        }
        js = ('js/jquery.form.js', 'js/jquery.pageslide.js', 'js/jquery.colorbox-min.js', 'js/colorbox.coop.js')



class NewsletterSchedulingForm(floppyforms.ModelForm):
    class Meta:
        model = NewsletterSending
        fields = ('scheduling_dt',)

    def clean_scheduling_dt(self):
        sch_dt = self.cleaned_data['scheduling_dt']

        if not sch_dt:
            raise ValidationError(_(u"This field is required"))

        if sch_dt < datetime.now():
            raise ValidationError(_(u"The scheduling date must be in future"))
        return sch_dt


class NewsletterTemplateForm(forms.Form):

    def __init__(self, newsletter, user, *args, **kwargs):
        super(NewsletterTemplateForm, self).__init__(*args, **kwargs)
        choices = get_newsletter_templates(newsletter, user)
        # if choices:
        self.fields["template"] = forms.ChoiceField(choices=choices)
        # else:
        #     self.fields["template"] = forms.CharField()
        self.fields["template"].initial = newsletter.template


