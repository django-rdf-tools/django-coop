# -*- coding:utf-8 -*-

# from coop.place.forms import BaseSiteForm
# import models
# 
# class SiteForm(BaseSiteForm):
#     class Meta:
#         model = models.Site
# 

import floppyforms as forms
from coop_cms.forms import ArticleForm as CmsArticleForm
from coop_cms.settings import get_article_class
from djaloha.widgets import AlohaInput

class ArticleForm(CmsArticleForm):
    class Meta:
        model = get_article_class()
        fields = ('title', 'content', 'logo', 'author')
        widgets = {
            'title': AlohaInput(),
            'content': AlohaInput(),
        }