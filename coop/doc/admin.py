# -*- coding:utf-8 -*-

from django.conf import settings
from django.contrib import admin
#from coop_local.models import Attached
from coop.utils.autocomplete_admin import FkAutocompleteAdmin, InlineAutocompleteAdmin, NoLookupsFkAutocompleteAdmin
from django.contrib.contenttypes.generic import GenericTabularInline
from django.utils.translation import ugettext_lazy as _
from django.db.models.loading import get_model
from media_tree.forms import FileForm
from media_tree.models import FileNode
from media_tree.widgets import AdminThumbWidget


class MyFileForm(FileForm):
    class Meta:
        fields = ['parent', 'file', 'title']
        widgets = {'file': AdminThumbWidget()}


class AttachmentsInline(GenericTabularInline):
    model = get_model('coop_local','Attachment')
    form = MyFileForm
    verbose_name = _(u'Attachment')
    verbose_name_plural = _(u'Attachements')
    extra = 1


# from media_tree.forms import UploadForm

# class AttachedInline(GenericTabularInline):
# 	model = 'media_tree.FileNode'
# 	form = UploadForm
#     verbose_name = _(u'Attachment')
#     verbose_name_plural = _(u'Attachements')
#     extra = 1