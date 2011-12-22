from django import template
from urlparse import urlparse, urlunparse

register = template.Library()

@register.simple_tag
def favicon(url):
    parsed_url = urlparse(url)

    return urlunparse((parsed_url[0], parsed_url[1],
                       u'favicon.ico', parsed_url[3],
                       parsed_url[4], parsed_url[5]))