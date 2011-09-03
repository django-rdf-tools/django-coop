from django import forms
from models import Schema, MappedModel, SchemaClass, SchemaProperty, MappedField
from utils import get_mappable_content_types
from django.utils.translation import ugettext as _



class MappableModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MappableModelForm, self).__init__(*args, **kwargs)
        # self.fields['rdf_class'].widget = GroupedModelChoiceField(
        #                 queryset=SchemaClass.objects.all().order_by('schema__prefix'),
        #                 group_by_field='schema')
        self.fields['model_name'].widget = forms.Select(choices=get_mappable_content_types())
        #self.fields['rdf_class'].widget = forms.Select(choices=get_rdf_classes())
        
    class Meta:
        model = MappedModel

# 
# def get_rdf_properties():              
#     AVAILABLE_PROPERTIES = []
#     for s in Schema.objects.all().order_by('prefix'):
#         AVAILABLE_PROPERTIES.append((
#             s.prefix+':', 
#             tuple((x.id,x.prop_label) for x in SchemaProperty.objects.filter(schema=s))
#         ))
#     return AVAILABLE_PROPERTIES

def get_fields_from_model(model):
    AVAILABLE_FIELDS =[]
    for f in model.model_class()._meta.fields:
        AVAILABLE_FIELDS.append( (f.name,unicode(f.verbose_name)))
    return AVAILABLE_FIELDS


class MappedFieldForm(forms.ModelForm):
    class Meta:
        model = MappedField
    def __init__(self,*args,**kwargs):
        super(MappedFieldForm, self).__init__(*args,**kwargs)
        self.fields['field_name'].widget = forms.Select(choices=get_fields_from_model(self.instance.model.model_name))

