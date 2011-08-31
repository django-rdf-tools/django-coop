# -*- coding:utf-8 -*-
from django.contrib import admin
from d2rq.models import Schema,SchemaClass,SchemaProperty,MappedModel,MappedField
from django import forms
from forms import MappableModelForm


class MappableModelAdmin(admin.ModelAdmin):
    form = MappableModelForm
    
admin.site.register(MappedModel, MappableModelAdmin)


class ClassInline(admin.TabularInline):
    model = SchemaClass
    extra=0

class PropertyInline(admin.TabularInline):
    model = SchemaProperty
    extra=0

class SchemaAdmin(admin.ModelAdmin):
    list_display = ('prefix','label','link_in_admin',)
    list_display_links =('prefix','label')
    ordering = ('prefix',)
    inlines = [
            ClassInline,PropertyInline
        ]
admin.site.register(Schema,SchemaAdmin)

class OntologySelectWidget(forms.Select):
    pass
    

class ClassPropAdminForm(forms.ModelForm):
    class Meta:
        model = MappedField
    def __init__(self,*args,**kwargs):
        super(ClassPropAdminForm, self).__init__(*args,**kwargs)
        #qs = MyModel.objects.exclude(pk = self.instance.pk) #grab instance.pk here
        self.widgets = {
            'class_prop' : OntologySelectWidget(choices=ontology_get_list(self.instance.uri,self.instance.prefix),)
        }



