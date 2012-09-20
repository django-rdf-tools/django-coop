# -*- coding:utf-8 -*-

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