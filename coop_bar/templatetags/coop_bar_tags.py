# -*- coding: utf-8 -*-

from django import template
from django.template.loader import get_template
from django.template import Context
register = template.Library()
from coop_bar import CoopBar

class CoopBarNode(template.Node):
    
    def render(self, context):
        request = context["request"]
        commands = CoopBar().get_commands(request, context)
        if commands: #hide admin-bar if nothing to display
            t = get_template("coop_bar.html")
            return t.render(Context({'commands': commands}))
        return u''

@register.tag
def coop_bar(parser, token):
    return CoopBarNode()

class CoopBarHeaderNode(template.Node):
    def render(self, context):
        STATIC_URL = context["STATIC_URL"]
        return u'<link rel="stylesheet" href="{0}css/coop_bar.css" type="text/css" />'.format(STATIC_URL)

@register.tag
def coop_bar_headers(parser, token):
    return CoopBarHeaderNode()

