# -*- coding: utf-8 -*-

from django import template
from django.template.loader import get_template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from coop_tree.models import NavNode
from django.contrib.contenttypes.models import ContentType

register = template.Library()

class NavigationAsNestedUlNode(template.Node):
   def render(self, context):
      root_nodes = NavNode.objects.filter(parent__isnull=True).order_by("ordering")
      return u''.join([node.as_li() for node in root_nodes])

@register.tag
def navigation_as_nested_ul(parser, token):
   return NavigationAsNestedUlNode()

class NavigationBreadcrumbNode(template.Node):
   def render(self, context):
      object = context.get("object")
      ct=ContentType.objects.get_for_model(object.__class__)
      nav_nodes = NavNode.objects.filter(content_type=ct, object_id=object.id)
      if nav_nodes.count()>0:
         return nav_nodes[0].as_breadcrumb()
      return u''

@register.tag
def navigation_breadcrumb(parser, token):
   return NavigationBreadcrumbNode()

class NavigationChildrenNode(template.Node):
   def render(self, context):
      object = context.get("object")
      ct=ContentType.objects.get_for_model(object.__class__)
      nav_nodes = NavNode.objects.filter(content_type=ct, object_id=object.id)
      if nav_nodes.count()>0:
         return nav_nodes[0].children_as_li()
      return u''

@register.tag
def navigation_children(parser, token):
   return NavigationChildrenNode()

class NavigationSiblingsNode(template.Node):
   def render(self, context):
      object = context.get("object")
      ct=ContentType.objects.get_for_model(object.__class__)
      nav_nodes = NavNode.objects.filter(content_type=ct, object_id=object.id)
      if nav_nodes.count()>0:
         return nav_nodes[0].siblings_as_li()
      return u''

@register.tag
def navigation_siblings(parser, token):
   return NavigationSiblingsNode()
