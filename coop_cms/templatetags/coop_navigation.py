# -*- coding: utf-8 -*-

from django import template
from django.template.loader import get_template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from coop_cms.models import NavNode
from django.contrib.contenttypes.models import ContentType
register = template.Library()
from django.template import VariableDoesNotExist

def extract_kwargs(args):
   kwargs = {}
   for arg in args:
      try:
         key, value = arg.split('=')
         kwargs[key] = value
      except ValueError: #No = in the arg
         pass
   return kwargs

class NavigatationTemplateNode(template.Node):
   def __init__(self, *args, **kwargs):
      super(NavigatationTemplateNode, self).__init__()
      self._kwargs = {}
      for (k, v) in kwargs.items():
         self._kwargs[k] = template.Variable(v)
   
   def format_css_class(self, class_name):
      return u' class="{0}"'.format(class_name) if class_name else u""

   def resolve_kwargs(self, context):
      kwargs = {}
      for (k, v) in self._kwargs.items():
         try:
            kwargs[k] = v.resolve(context)
         except VariableDoesNotExist:
            kwargs[k] = v.var #if the variable can not be resolved, thake the value as is
         
         if k=='css_class':
            kwargs[k] = self.format_css_class(v)

      return kwargs

#----------------------------------------------------------
class NavigationAsNestedUlNode(NavigatationTemplateNode):
   
   def __init__(self, **kwargs):
      super(NavigationAsNestedUlNode, self).__init__(**kwargs)
   
   def render(self, context):
      kwargs = self.resolve_kwargs(context)
      root_nodes = NavNode.objects.filter(parent__isnull=True).order_by("ordering")
      return u''.join([node.as_navigation(**kwargs) for node in root_nodes])

@register.tag
def navigation_as_nested_ul(parser, token):
   args = token.contents.split()
   kwargs = extract_kwargs(args)
   return NavigationAsNestedUlNode(**kwargs)

#----------------------------------------------------------


class NavigationBreadcrumbNode(NavigatationTemplateNode):
   def __init__(self, object, **kwargs):
      super(NavigationBreadcrumbNode, self).__init__(**kwargs)
      self.object_var = template.Variable(object)

   def render(self, context):
      object = self.object_var.resolve(context)
      ct=ContentType.objects.get_for_model(object.__class__)
      nav_nodes = NavNode.objects.filter(content_type=ct, object_id=object.id)
      kwargs = self.resolve_kwargs(context)
      if nav_nodes.count()>0:
         return nav_nodes[0].as_breadcrumb(**kwargs)
      return u''

@register.tag
def navigation_breadcrumb(parser, token):
   args = token.contents.split()
   kwargs = extract_kwargs(args)
   if len(args) < 2:
       raise template.TemplateSyntaxError(_("navigation_breadcrumb requires object as argument"))
   return NavigationBreadcrumbNode(args[1], **kwargs)

class NavigationChildrenNode(NavigatationTemplateNode):

   def __init__(self, object, **kwargs):
      super(NavigationChildrenNode, self).__init__(**kwargs)
      self.object_var = template.Variable(object)

   def render(self, context):
      object = self.object_var.resolve(context)
      ct=ContentType.objects.get_for_model(object.__class__)
      nav_nodes = NavNode.objects.filter(content_type=ct, object_id=object.id)
      kwargs = self.resolve_kwargs(context)
      if nav_nodes.count()>0:
         return nav_nodes[0].children_as_navigation(**kwargs)
      return u''

@register.tag
def navigation_children(parser, token):
   args = token.contents.split()
   kwargs = extract_kwargs(args)
   if len(args) < 2:
       raise template.TemplateSyntaxError(_("navigation_children requires object as argument"))
   return NavigationChildrenNode(args[1], **kwargs)

class NavigationSiblingsNode(NavigatationTemplateNode):
   
   def __init__(self, object, **kwargs):
      super(NavigationSiblingsNode, self).__init__(**kwargs)
      self.object_var = template.Variable(object)
      
   def render(self, context):
      object = self.object_var.resolve(context)
      ct=ContentType.objects.get_for_model(object.__class__)
      nav_nodes = NavNode.objects.filter(content_type=ct, object_id=object.id)
      kwargs = self.resolve_kwargs(context)
      if nav_nodes.count()>0:
         return nav_nodes[0].siblings_as_navigation(**kwargs)
      return u''

@register.tag
def navigation_siblings(parser, token):
   args = token.contents.split()
   kwargs = extract_kwargs(args)
   if len(args) < 2:
       raise template.TemplateSyntaxError(_("navigation_siblings requires object as argument"))
   return NavigationSiblingsNode(args[1], **kwargs)
