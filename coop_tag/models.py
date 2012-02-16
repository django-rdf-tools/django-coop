# -*- coding:utf-8 -*-
from django.db import models
from taggit.models import TagBase, GenericTaggedItemBase
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

class Ctag(TagBase):
    '''
    Defines a Common Tag resource
    '''
    # FIELDS name and slug are defined in TagBase    
    language    = models.CharField(_(u'language'),max_length=10, default='fr')
    user        = models.ForeignKey(User,blank=True,null=True,verbose_name=_(u'django user'),editable=False)
    uri         = models.CharField(_(u'tag URI'),blank=True,max_length=250,editable=False)
    author_uri  = models.CharField(_(u'author URI'),blank=True,max_length=250,editable=False)
    created     = exfields.CreationDateTimeField(_(u'created'))
    modified    = exfields.ModificationDateTimeField(_(u'modified'))
    def get_absolute_url(self):
        return reverse('tag_detail', args=[self.slug])
        
class CtaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey(Ctag, related_name="ctagged_items")


from django.contrib import admin
admin.site.register(Ctag)

# TODO better admin for tags