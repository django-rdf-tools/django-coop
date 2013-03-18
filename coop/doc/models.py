# -*- coding:utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.contenttypes import generic
from django_extensions.db import fields as exfields
from coop.models import URIModel
from django.core.urlresolvers import reverse
import rdflib
from sorl.thumbnail import ImageField
from sorl.thumbnail import default
from media_tree.models import FileNode
from django.conf import settings


class BaseResourceCategory(models.Model):
    """
    Site web
    Flux Internet (RSS, twitter, etc)
    Livre
    Livre audio
    Revue
    Vidéo en ligne
    Documentaire vidéo
    Film
    Article de presse
    Guide méthodologique
    Rapport
    Autre document
    """
    label = models.CharField(blank=True, max_length=100)
    slug = exfields.AutoSlugField(populate_from=('label'), overwrite=True)
    description = models.TextField(_(u'description'), blank=True)

    class Meta:
        abstract = True
        verbose_name = _(u'resource category')
        verbose_name_plural = _(u'resource categories')
        app_label = 'coop_local'

    def __unicode__(self):
        return self.label





class BaseDocResource(URIModel):
    logo = ImageField(upload_to='logos/', null=True, blank=True)
    #temp_logo = models.ImageField(upload_to=get_logo_folder, blank=True, null=True, default='')
    label = models.CharField(_('label'), blank=True, max_length=250)
    slug = exfields.AutoSlugField(populate_from='label', blank=True, overwrite=True)
    description = models.TextField(_(u'description'), blank=True)
    notes = models.TextField(_(u'practical details'), blank=True)

    price = models.FloatField()
    page_url = models.URLField(_(u'web page'), blank=True, null=True)
    file_url = models.URLField(_(u'download link'), blank=True, null=True)

    category = models.ManyToManyField('coop_local.ResourceCategory', blank=True, null=True,
                                      verbose_name=_(u'resource category'))

    organization = models.ForeignKey('coop_local.Organization', verbose_name=_(u"organization / editor"), related_name="resource_organizer")
    person = models.ForeignKey('coop_local.Person', verbose_name=_(u'author'), related_name='resource_author')
    # We could also link to remote objects
    remote_person_uri = models.URLField(_(u'remote person URI'), blank=True, max_length=255)
    remote_person_label = models.CharField(_(u'remote person label'),
                                           max_length=250, blank=True, null=True,
                                           help_text=_(u'fill this only if the person record is not available locally'))
    remote_organization_uri = models.URLField(_(u'remote organization URI'), blank=True, max_length=255)
    remote_organization_label = models.CharField(_(u'remote organization label'),
                                                 max_length=250, blank=True, null=True,
                                                 help_text=_(u'fill this only if the organization record is not available locally'))

    zone = models.ForeignKey('coop_local.Area', verbose_name=_(u"geographic zone"), null=True, blank=True)

    if "coop.doc" in settings.INSTALLED_APPS:
        attachments = generic.GenericRelation('coop_local.Attachment')

    class Meta:
        verbose_name = _('documentary resource')
        verbose_name_plural = _('documentary resources')
        abstract = True
        app_label = 'coop_local'

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('resource-detail', args=[self.slug])

    def logo_list_display(self):
        try:
            if self.logo:
                thumb = default.backend.get_thumbnail(self.logo.file, settings.ADMIN_THUMBS_SIZE)
                return '<img width="%s" src="%s" />' % (thumb.width, thumb.url)
            else:
                return _(u"No Image")
        except IOError:
            return _(u"No Image")
    logo_list_display.short_description = _(u"logo")
    logo_list_display.allow_tags = True

    # this kind of function should be factorized, as well as the remote_{uri|label} field
    def organization_display(self):
        if not self.organization:
            if not self.remote_organization_label:
                return None
            else:
                return self.remote_organization_label
        else:
            return self.organization.label()

    organization_display.short_description = _(u"organization / editor")


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











