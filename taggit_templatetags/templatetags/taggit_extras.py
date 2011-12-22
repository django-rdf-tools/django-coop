from django import template
from django.db import models
from django.db.models import Count
from django.core.exceptions import FieldError
from django.db.models.loading import get_model

from templatetag_sugar.register import tag
from templatetag_sugar.parser import Variable, Optional, Model, Required

from taggit import VERSION as TAGGIT_VERSION
from taggit.managers import TaggableManager
from taggit.models import TaggedItem, Tag
from taggit_templatetags import settings

T_MAX = getattr(settings, 'TAGCLOUD_MAX', 6.0)
T_MIN = getattr(settings, 'TAGCLOUD_MIN', 1.0)

register = template.Library()

def get_queryset(forvar=None):
    count_field = None
    if forvar is None:
        # get all tags
        queryset = settings.TAG_MODEL.objects.all()
    else:
        # extract app label and model name
        beginning, applabel, model = None, None, None
        try:
            beginning, applabel, model = forvar.rsplit('.', 2)
        except ValueError:
            try:
                applabel, model = forvar.rsplit('.', 1)
            except ValueError:
                applabel = forvar
        applabel = applabel.lower()
        
        # filter tagged items  
        if model is None:
            # Get tags for a whole app
            queryset = settings.TAGGED_ITEM_MODEL.objects.filter(content_type__app_label=applabel)
            tag_ids = queryset.values_list('tag_id', flat=True)
            queryset = Tag.objects.filter(id__in=tag_ids)
        else:
            # Get tags for a model
            model = model.lower()
            if ":" in model:
                model, manager_attr = model.split(":", 1)
            else:
                manager_attr = "tags"
            model_class = get_model(applabel, model)
            manager = getattr(model_class, manager_attr)
            queryset = manager.all()
            through_opts = manager.through._meta
            count_field = ("%s_%s_items" % (through_opts.app_label,
                    through_opts.object_name)).lower()

    if count_field is None:
        relname = settings.TAGGED_ITEM_MODEL._meta.get_field_by_name('tag')[0].rel.related_name
        return queryset.annotate(num_times=Count(relname))
    else:
        return queryset.annotate(num_times=Count(count_field))



def get_weight_fun(t_min, t_max, f_min, f_max):
    def weight_fun(f_i, t_min=t_min, t_max=t_max, f_min=f_min, f_max=f_max):
        # Prevent a division by zero here, found to occur under some
        # pathological but nevertheless actually occurring circumstances.
        if f_max == f_min:
            mult_fac = 1.0
        else:
            mult_fac = float(t_max-t_min)/float(f_max-f_min)
            
        return t_max - (f_max-f_i)*mult_fac
    return weight_fun

@tag(register, {Required('asvar'): Variable(), Optional('for'): Variable(), Optional('count'): Variable()}) 
def get_taglist(context, asvar, forvar=None, count=None):
    queryset = get_queryset(forvar)         
    queryset = queryset.order_by('-num_times')        
    if count:
        context[asvar] = queryset[:int(count)]
    else:
        context[asvar] = queryset
        
    return ''

@tag(register, {Optional('as'): Variable(), Optional('for'): Variable(), Optional('count'): Variable()})
def get_tagcloud(context, asvar=None, forvar=None, count=None):
    queryset = get_queryset(forvar)
    num_times = queryset.values_list('num_times', flat=True)
    if(len(num_times) == 0):
        context[asvar] = queryset
        return ''
    weight_fun = get_weight_fun(T_MIN, T_MAX, min(num_times), max(num_times))
    if count:
        queryset = queryset.order_by('name')[:int(count)-1]
    else:
        queryset = queryset.order_by('name')
    for tag in queryset:
        tag.weight = weight_fun(tag.num_times)
    context[asvar] = queryset
    return ''
    
def include_tagcloud(forvar=None):
    return {'forvar': forvar}

def include_taglist(forvar=None):
    return {'forvar': forvar}
  
register.inclusion_tag('taggit_templatetags/taglist_include.html')(include_taglist)
register.inclusion_tag('taggit_templatetags/tagcloud_include.html')(include_tagcloud)
