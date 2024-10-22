# -*- coding:utf-8 -*-

from django.conf import settings
import floppyforms as forms
from coop_cms.forms import ArticleForm as CmsArticleForm
from coop_cms.settings import get_article_class
from djaloha.widgets import AlohaInput


class ArticleForm(CmsArticleForm):
    class Meta:
        model = get_article_class()
        fields = ('title', 'summary', 'content', 'logo')
        widgets = {
            'title': AlohaInput(text_color_plugin=False),
            'summary': AlohaInput(text_color_plugin=False),
            'content': AlohaInput(text_color_plugin=False),
        }


if 'haystack' in settings.INSTALLED_APPS:
    from haystack.forms import SearchForm


    class SiteSearchForm(SearchForm):
        def set_site(self, site):
            self.site = site

        def search(self):
            # First, store the SearchQuerySet received from other processing.
            sqs = super(SiteSearchForm, self).search()
            sqs = sqs.filter(sites__contains=self.site.domain)

            return sqs


class PersonContact(forms.Form):
    sender = forms.EmailField(label='Votre e-mail')
    message = forms.CharField(widget=forms.Textarea, label='Votre message')

