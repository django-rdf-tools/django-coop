# -*- coding: utf-8 -*-

from django import template
from django.template.loader import get_template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from coop_cms.models import NavNode
from django.contrib.contenttypes.models import ContentType
register = template.Library()

class NavigationAsNestedUlNode(template.Node):
   def render(self, context):
      root_nodes = NavNode.objects.filter(parent__isnull=True).order_by("ordering")
      return u''.join([node.as_li() for node in root_nodes])

@register.tag
def navigation_as_nested_ul(parser, token):
   args = token.contents.split()
   if len(args) != 1:
       raise template.TemplateSyntaxError(_("navigation_as_nested_ul has no argument"))
       
   return NavigationAsNestedUlNode()

@register.tag
def navigation_as_nested_ul(parser, token):
   args = token.contents.split()
   if len(args) != 1:
       raise template.TemplateSyntaxError(_("navigation_as_nested_ul has no argument"))
       
   return NavigationAsNestedUlNode()


class NavigationBreadcrumbNode(template.Node):
   def __init__(self, object):
      super(NavigationBreadcrumbNode, self).__init__()
      self.object_var = template.Variable(object)

   def render(self, context):
      object = self.object_var.resolve(context)
      ct=ContentType.objects.get_for_model(object.__class__)
      nav_nodes = NavNode.objects.filter(content_type=ct, object_id=object.id)
      if nav_nodes.count()>0:
         return nav_nodes[0].as_breadcrumb()
      return u''

@register.tag
def navigation_breadcrumb(parser, token):
   args = token.contents.split()
   if len(args) != 2:
       raise template.TemplateSyntaxError(_("navigation_breadcrumb requires object as argument"))

   return NavigationBreadcrumbNode(args[1])

class NavigationChildrenNode(template.Node):

   def __init__(self, object):
      super(NavigationChildrenNode, self).__init__()
      self.object_var = template.Variable(object)

   def render(self, context):
      object = self.object_var.resolve(context)
      ct=ContentType.objects.get_for_model(object.__class__)
      nav_nodes = NavNode.objects.filter(content_type=ct, object_id=object.id)
      if nav_nodes.count()>0:
         return nav_nodes[0].children_as_li()
      return u''

@register.tag
def navigation_children(parser, token):
   args = token.contents.split()
   if len(args) != 2:
       raise template.TemplateSyntaxError(_("navigation_children requires object as argument"))
   return NavigationChildrenNode(args[1])

class NavigationSiblingsNode(template.Node):
   
   def __init__(self, object):
      super(NavigationSiblingsNode, self).__init__()
      self.object_var = template.Variable(object)
   
   def render(self, context):
      object = self.object_var.resolve(context)
      ct=ContentType.objects.get_for_model(object.__class__)
      nav_nodes = NavNode.objects.filter(content_type=ct, object_id=object.id)
      if nav_nodes.count()>0:
         return nav_nodes[0].siblings_as_li()
      return u''

@register.tag
def navigation_siblings(parser, token):
   args = token.contents.split()
   if len(args) != 2:
       raise template.TemplateSyntaxError(_("navigation_siblings requires object as argument"))
   return NavigationSiblingsNode(args[1])
