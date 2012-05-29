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


class LocalRemoteUrlNode(template.Node):

    def __init__(self, obj, model_name):
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
            return related.get_absolute_url()
        else:
            try:
                return object.__getattribute__(self.model_name + '_uri')
            except AttributeError:
                raise FieldError('Field %s_uri is not present on %s' % (self.model_name, object))



@register.tag
def local_or_remote_url(parser, token):
    try:
        tag_name, obj, model_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "This tag requires two arguments" 
    #TODO verifier ce qu'on a
    return LocalRemoteUrlNode(obj, model_name)




