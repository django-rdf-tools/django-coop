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

    def __init__(self, attr, obj, model_name):
        self.attr = attr
        self.obj = template.Variable(obj)
        self.model_name = model_name

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
            if self.attr == 'uri':
                return related.get_absolute_url()
            elif self.attr == 'label':
                return related.label()
        else:
            try:
                return object.__getattribute__(self.model_name + '_' + self.attr)
            except AttributeError:
                raise FieldError('Field %s_%s is not present on %s' % (self.model_name, self.attr, object))



@register.tag
def local_or_remote(parser, token):
    try:
        method_name, tag_name, obj, model_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "This tag requires three arguments : object, uri or label, linked model name"
    #TODO verifier ce qu'on a
    return LocalRemoteNode(tag_name, obj, model_name)




