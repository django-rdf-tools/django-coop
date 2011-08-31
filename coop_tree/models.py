# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.template.loader import get_template
from django.template import Context
from django.core.urlresolvers import reverse

class Url(models.Model):
    """A url. This is a content: Maybe misplaced. Included in his own app?"""
    url = models.URLField()
    
    def get_absolute_url(self):
        return self.url
    
    def get_label(self):
        if self.url.find('http://')==0:
            return self.url[7:]
        return self.url
    
    def __unicode__(self):
        return self.url

class NavigableType(models.Model):
    
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
    search_field = models.CharField(max_length=200)
    label_rule = models.IntegerField(verbose_name=_(u'How to generate the label'),
        choices=LABEL_RULE_CHOICES, default=LABEL_USE_SEARCH_FIELD)
    
    def __unicode__(self):
        return self.content_type.app_label+'.'+self.content_type.model

    
class NavNode(models.Model):
    """
    A navigation node
    Part of the tree as child of his parent
    Point on a content_object 
    """
    label = models.CharField(max_length=200)
    
    parent = models.ForeignKey("NavNode", blank=True, null=True, default=0)
    ordering = models.PositiveIntegerField(default=0)
    
    #generic relation
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    def get_absolute_url(self):
        return self.content_object.get_absolute_url()
    
    def get_content_name(self):
        return self.content_type.model_class()._meta.verbose_name
    
    def __unicode__(self):
        return self.label
    
    class Meta:
        verbose_name = _(u'navigation node')
        verbose_name_plural = _(u'navigation nodes')
    
    def get_children(self):
        return NavNode.objects.filter(parent=self).order_by("ordering")
        
    def get_siblings(self):
        return NavNode.objects.filter(parent=self.parent).order_by("ordering")
        
    def as_li(self):
        #Display the node and his children as nested ul and li html tags.
        #Render from a template who is in charge of rendering children
        #This prints the whole tree recursively
        t = get_template('coop_tree/_node_li.html')
        return t.render(Context({'node': self}))
        
    def as_breadcrumb(self):
        t = get_template('coop_tree/_node_breadcrumb.html')
        return t.render(Context({'node': self}))

    def children_as_li(self):
        t = get_template('coop_tree/_node_children_li.html')
        return t.render(Context({'node': self}))
        
    def siblings_as_li(self):
        t = get_template('coop_tree/_node_sibling_li.html')
        return t.render(Context({'node': self}))
        

    
class NavTree(models.Model):
    last_update = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = verbose_name = _(u'Navigation tree')
