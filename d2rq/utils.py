from django.contrib.contenttypes.models import ContentType
import config # not unused, needed by livesettings !
from livesettings import config_value
from d2rq.models import Schema

def get_mappable_content_types():
    done = []
    AVAILABLE_MODELS = []
    all_models = ContentType.objects.filter(app_label__in=config_value('d2rq','MAPPED_APPS')).order_by('app_label')
    for m in all_models:
        if(m.app_label not in done):
            AVAILABLE_MODELS.append((
                m.app_label , 
                tuple((x.id,x.name) for x in all_models.filter(app_label=m.app_label))
                ))
            done.append(m.app_label)
    return AVAILABLE_MODELS


# alternative pour faire des menus select sur fkey avec optgroup
# http://djangosnippets.org/snippets/1968/

#-*- coding: utf-8 -*- 
#!/usr/bin/env python

from django.db import models
from django.contrib.admin.filterspecs import FilterSpec, ChoicesFilterSpec
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext as _

class FkFilterSpec(ChoicesFilterSpec):
    def __init__(self, f, request, params, model, *args, **kwargs):
        super(FkFilterSpec, self).__init__(f, request, params, model, *args, **kwargs)
        
        # ******* Extract parameters ********
        the_args = f.fk_filterspec.copy() 
        #The field of the related table
        fk_field = the_args['fk_field'] 
        
        #The name in the related table to use as label in the choices
        label = the_args.pop('label', '')
        
        #a title: by default the lookup arg
        self.filter_title = the_args.pop('title', '')
        
        #the foreign key field. By default the field the filter is assigned
        fk = the_args.pop('fk', f.name) 
        
        # ******* Build the filter definition ********
        
        self.lookup_kwarg = '{0}__{1}'.format(fk, fk_field)
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        self.lookup_labels = {}
        #get the list of values
        values_list = model.objects.values_list(self.lookup_kwarg, flat=True)
        #get the 
        if label:
            label_field = '{0}__{1}__{2}'.format(fk, fk_field, label)
        else:
            label_field = '{0}__{1}'.format(fk, fk_field)
        labels = model.objects.values_list(label_field, flat=True)
        for (v, l) in zip(values_list, labels):
            self.lookup_labels[v] = l
        self.lookup_choices = self.lookup_labels.keys()

    def choices(self, cl):
        yield {'selected': self.lookup_val is None,
                'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
                'display': _('All')}
        for val in self.lookup_choices:
            yield {'selected': smart_unicode(val) == self.lookup_val,
                    'query_string': cl.get_query_string({self.lookup_kwarg: val}),
                    'display': smart_unicode(self.lookup_labels[val])}
    
    def title(self):
        if self.filter_title:
            return self.filter_title
        else:
            return super(FkFilterSpec, self).title()

    @classmethod
    def register_filterspec(cls):
        """register the filter. To be called in the models.py"""
        FilterSpec.filter_specs.insert(0,
            (lambda f: len(getattr(f, 'fk_filterspec', [])), cls)
        )


