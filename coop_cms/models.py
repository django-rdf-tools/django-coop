# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.template.loader import get_template
from django.template import Context
from django_extensions.db.models import TimeStampedModel, AutoSlugField
from django.conf import settings
from sorl.thumbnail import default as sorl_thumbnail
import os.path

class NavType(models.Model):
    
    LABEL_USE_UNICODE = 0
    LABEL_USE_SEARCH_FIELD = 1
    LABEL_USE_GET_LABEL = 2
    
    LABEL_RULE_CHOICES = (
        (LABEL_USE_UNICODE, _(u'Use object unicode')),
        (LABEL_USE_SEARCH_FIELD, _(u'Use search field')),
        (LABEL_USE_GET_LABEL, _(u'Use get_label')),
    )
    
    """Define which ContentTypes can be inserted in the tree as content"""
    content_type = models.ForeignKey(ContentType, unique=True)
    search_field = models.CharField(max_length=200, blank=True, default="")
    label_rule = models.IntegerField(verbose_name=_(u'How to generate the label'),
        choices=LABEL_RULE_CHOICES, default=LABEL_USE_SEARCH_FIELD)
    
    def __unicode__(self):
        return self.content_type.app_label+'.'+self.content_type.model

    class Meta:
        verbose_name = _(u'navigable type')
        verbose_name_plural = _(u'navigable types')

    
class NavNode(models.Model):
    """
    A navigation node
    Part of the tree as child of his parent
    Point on a content_object 
    """
    label = models.CharField(max_length=200, verbose_name=_("label"))
    
    parent = models.ForeignKey("NavNode", blank=True, null=True, default=0, verbose_name=_("parent"))
    ordering = models.PositiveIntegerField(_("ordering"), default=0)
    
    #generic relation
    content_type = models.ForeignKey(ContentType, verbose_name=_("content_type"))
    object_id = models.PositiveIntegerField(verbose_name=_("object id"))
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    in_navigation = models.BooleanField(_("in navigation"), default=True)
    
    def get_absolute_url(self):
        return self.content_object.get_absolute_url()
    
    def get_content_name(self):
        return self.content_type.model_class()._meta.verbose_name
    
    def __unicode__(self):
        return self.label
    
    class Meta:
        verbose_name = _(u'navigation node')
        verbose_name_plural = _(u'navigation nodes')
    
    def get_children(self, in_navigation=None):
        nodes = NavNode.objects.filter(parent=self).order_by("ordering")
        if in_navigation != None:
            nodes = nodes.filter(in_navigation=in_navigation)
        return nodes
        
    def get_siblings(self, in_navigation=None):
        nodes = NavNode.objects.filter(parent=self.parent).order_by("ordering")
        if in_navigation != None:
            nodes = nodes.filter(in_navigation=in_navigation)
        return nodes
    
    def as_jstree(self):
        li_content = u'<a href="{0}">{1}</a>'.format(self.get_absolute_url(), self.label)
        
        children_li = [child.as_jstree() for child in self.get_children()]
        
        return u'<li id="node_{0}" rel={3}>{1}<ul>{2}</ul></li>'.format(
            self.id, li_content, u''.join(children_li), "in_nav" if self.in_navigation else "out_nav"
        )
    
    def _get_li_content(self, li_template):
        if li_template:
            t = get_template(li_template) if type(li_template) is unicode else li_template
            return t.render(Context({'node': self}))
        else:
            return u'<a href="{0}">{1}</a>'.format(self.get_absolute_url(), self.label)
    
    def as_navigation(self, li_template=None, css_class=""):
        #Display the node and his children as nested ul and li html tags.
        #li_template is a custom template that can be passed
        
        if not self.in_navigation:
            return ""
        
        children_li = [child.as_navigation(li_template) for child in self.get_children(in_navigation=True)]
        children_html = u"<ul>{0}</ul>".format(u''.join(children_li)) if children_li else ""
        
        return u'<li{0}>{1}{2}</li>'.format(css_class, self._get_li_content(li_template), children_html)
        
    def as_breadcrumb(self, li_template=None, css_class=""):
        html = self.parent.as_breadcrumb(li_template) if self.parent else u""
        return html + u'<li{0}>{1}</li>'.format(css_class, self._get_li_content(li_template))

    def children_as_navigation(self, li_template=None, css_class=""):
        children_li = [u'<li{0}>{1}</li>'.format(css_class, child._get_li_content(li_template))
            for child in self.get_children(in_navigation=True)]
        return  u''.join(children_li)
        
    def siblings_as_navigation(self, li_template=None, css_class=""):
        siblings_li = [u'<li{0}>{1}</li>'.format(css_class, sibling._get_li_content(li_template))
            for sibling in self.get_siblings(in_navigation=True)]
        return  u''.join(siblings_li)
        
    
class NavTree(models.Model):
    last_update = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = verbose_name = _(u'Navigation tree')

class Article(TimeStampedModel):
    """An article : static page, blog item, ..."""
    slug = AutoSlugField(populate_from='title', max_length=100, unique=True)
    title = models.TextField(_(u'title'), default=_('Page title'))
    content = models.TextField(_(u'content'), default=_('Page content'))
        
    class Meta:
        verbose_name = _(u"article")
        verbose_name_plural = _(u"articles")
    
    def __unicode__(self):
        return self.slug
    
    def get_label(self):
        return self.title
    
    def get_absolute_url(self):
        return u'/'+self.slug
    
class Link(TimeStampedModel):
    """Link to a given url"""
    url = models.URLField()
    
    def get_absolute_url(self):
        return self.url
    
    def get_label(self):
        if self.url.find('http://')==0:
            return self.url[7:]
        return self.url
    
    def __unicode__(self):
        return self.url

    class Meta:
        verbose_name = _(u"link")
        verbose_name_plural = _(u"links")

def get_doc_folder(instance, filename):
    try:
        doc_root = settings.DOCUMENT_FOLDER
    except AttributeError:
        doc_root = 'doc'
        
    return u'{0}/{1}/{2}'.format(doc_root,
        instance.created.strftime('%Y%d%m%H%M%S'), filename)

def get_img_folder(instance, filename):
    try:
        img_root = settings.IMAGE_FOLDER
    except AttributeError:
        img_root = 'img'
        
    return u'{0}/{1}/{2}'.format(img_root,
        instance.created.strftime('%Y%d%m%H%M%S'), filename)

class Media(TimeStampedModel):
    name = models.CharField(_('name'), max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True

class Image(Media):
    file = models.ImageField(_('file'), upload_to=get_img_folder)
    
    def as_thumbnail(self):
        return sorl_thumbnail.backend.get_thumbnail(self.file.file, "200x100", crop='center')

class Document(Media):
    file = models.FileField(_('file'), upload_to=get_doc_folder)

    def get_ico_url(self):
        root, ext = os.path.splitext(self.file.name)
        ext = ext[1:] #remove leading dot
        if ext in ('pdf', 'doc', 'xls', 'txt'):
            return settings.STATIC_URL+u'img/{0}.png'.format(ext)
        else:
            return settings.STATIC_URL+u'img/default-icon.png'

    
    
    