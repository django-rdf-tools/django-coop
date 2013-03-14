# -*- coding:utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


# class BaseAttached(models.Model):
#     # things which are linked to an event
    
#     attachment = models.ForeignKey('media_tree.FileNode', verbose_name=_(u"attachement"))
#     # generic key to other objects

#     content_type = models.ForeignKey(ContentType, blank=True, null=True, default=None)
#     object_id = models.PositiveIntegerField()
#     content_object = generic.GenericForeignKey('content_type', 'object_id')

#     def __unicode__(self):
#         return _(u"\"%(attachment)s\" link to \"%(thing)s\"") % {'attachment': unicode(self.attachment),
#                                                                  'thing': unicode(self.content_object)
#                                                                   }

#     class Meta:
#         abstract = True
#         verbose_name = _(u'Attached file')
#         verbose_name_plural = _(u'Attached files')
#         app_label = 'coop_local'


from media_tree.models import FileNode


class BaseAttachment(FileNode):

    content_type = models.ForeignKey('contenttypes.ContentType', blank=True, null=True, default=None)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _(u'Attached file')
        verbose_name_plural = _(u'Attached files')
        abstract = True
        app_label = 'coop_local'

    def save(self, *args, **kwargs):
        if not self.node_type:
            self.node_type = FileNode.FILE
        super(BaseAttachment, self).save(*args, **kwargs)


