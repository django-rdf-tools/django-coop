# -*- coding: utf-8 -*-

from django import template
register = template.Library()


@register.filter
def convert_linebreaks(value):
   s = value.replace('\r', '\\r')
   s = s.replace('\n', '\\n')
   return s
