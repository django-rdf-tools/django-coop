import datetime
from django.template.defaultfilters import stringfilter
import re
from django.template import Library

register = Library()

def replace_quote(string): 
    return re.sub(r"'", r'"', string)

register.filter('replace_quote', replace_quote)

from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.utils import simplejson


def jsonify(object):
    if isinstance(object, QuerySet):
        return serialize('json', object)
    return simplejson.dumps(object)

register.filter('jsonify', jsonify)