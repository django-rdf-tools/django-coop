# -*- coding:utf-8 -*-

from django import template
from urlparse import urlparse, urlunparse
from django.core.exceptions import FieldError
from django.db.models.fields import FieldDoesNotExist

register = template.Library()

@register.simple_tag
def favicon(url):
    parsed_url = urlparse(url)
    return urlunparse((parsed_url[0], parsed_url[1],
                       u'favicon.ico', parsed_url[3],
                       parsed_url[4], parsed_url[5]))


class LocalRemoteNode(template.Node):

    def __init__(self, attr, obj, model_name, as_var=None):
        self.attr = attr
        self.obj = template.Variable(obj)
        self.model_name = model_name
        if as_var:
            self.as_var = as_var

    def render(self, context):
        try:
            object = self.obj.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        try:
            object._meta.get_field_by_name(self.model_name)
        except(FieldDoesNotExist):
            raise template.TemplateSyntaxError('Unknown attribute for %s' % object)

        related = object.__getattribute__(self.model_name)
        if related:
            # l'objet a bien une Fkey vers le modele correspondant
            # on renvoie donc le champ lié demandé
            if self.attr == 'uri':
                res = related.get_absolute_url()
            elif self.attr == 'label':
                res = related.label()
        else:
            # pas de Fkey donc on cherche un champ remote_{nom du modèle lié}_uri
            try:
                fieldname = 'remote_' + self.model_name + '_' + self.attr
                res = object.__getattribute__(fieldname)
            except AttributeError:
                raise FieldError('Field remote_%s_%s is not present on %s, correct your templatetag call syntax or add the corresponding field' % (self.model_name, self.attr, object))
        if self.as_var:
            context[self.as_var] = res
            return u''
        else:
            return res


@register.tag
def local_or_remote(parser, token):

    contents = token.split_contents()
    params = contents[1:]
    try:
        if len(params) == 3:
            tag_name, obj, model_name = params
        elif len(params) == 5 and params[3] == u'as':
            tag_name, obj, model_name, as_param, as_var = params
            params.remove(u'as')
    except ValueError:
        raise template.TemplateSyntaxError, "This tag requires three arguments : object, uri or label, linked model name, and optional as parameter with a variable name"
    #TODO verifier ce qu'on a
    return LocalRemoteNode(*params)

