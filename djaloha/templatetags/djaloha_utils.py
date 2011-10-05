# -*- coding: utf-8 -*-

from django import template
register = template.Library()

@register.filter
def convert_crlf(value):
   """
   Replace carriage return and line feed character by their javascript value
   Make possible to include title with those characters in the aloha links
   """
   return value.replace('\r', '\\r').replace('\n', '\\n')
   
@register.filter
def remove_br(value):
   """
   Remove the <br> tag by spaces except at the end
   Used for providing title without this tag 
   """
   return value.replace('<br>', ' ').strip()
