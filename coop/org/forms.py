# -*- coding:utf-8 -*-
from django import forms
import floppyforms
import re
from coop_local.models import Organization
from djaloha.widgets import AlohaInput
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError


class OrganizationForm(floppyforms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
        self.org = kwargs.get('instance', None)
        #self.set_logo_size()

    class Meta:
        model = Organization
        fields = ('title', 'description', 'logo')
        widgets = {
            'title': AlohaInput(text_color_plugin=False),
            'description': AlohaInput(text_color_plugin=False),
        }

    # def set_logo_size(self, logo_size=None):
    #     thumbnail_src = self.logo_thumbnail(logo_size)
    #     update_url = reverse('coop_cms_update_logo', args=[self.article.id])
    #     self.fields['logo'].widget = ImageEdit(update_url, thumbnail_src.url if thumbnail_src else '')

    def logo_thumbnail(self, logo_size=None):
        if self.org:
            return self.org.logo_thumbnail(True, logo_size=logo_size)

    def clean_title(self):
        title = self.cleaned_data['title'].strip()
        if title[-4:].lower() == '<br>':
            title = title[:-4]
        if not title:
            raise ValidationError(_(u"Title can not be empty"))
        if re.search(u'<(.*)>', title):
            raise ValidationError(_(u'HTML content is not allowed in the title'))
        return title


