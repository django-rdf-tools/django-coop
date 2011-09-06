# -*- coding:utf-8 -*-
from django.contrib import admin
from d2rq.models import Schema,SchemaClass,SchemaProperty,MappedModel,MappedField
from django import forms
from forms import MappableModelForm, MappedFieldForm


class ClassInline(admin.StackedInline):
    model = SchemaClass
    extra=0

class PropertyInline(admin.StackedInline):
    model = SchemaProperty
    extra=0


class SchemaClassAdmin(admin.ModelAdmin):
    list_filter = ('schema__prefix',)
admin.site.register(SchemaClass,SchemaClassAdmin)

class SchemaPropertyAdmin(admin.ModelAdmin):
    list_filter = ('schema__prefix',)
admin.site.register(SchemaProperty,SchemaPropertyAdmin)


class SchemaAdmin(admin.ModelAdmin):
    list_display = ('prefix','label','vocab_type','format','link_in_admin',)
    list_display_links =('prefix','label')
    ordering = ('prefix',)
    
    #inlines = [ClassInline,PropertyInline]
admin.site.register(Schema,SchemaAdmin)


class MappedFieldInline(admin.StackedInline):
    form = MappedFieldForm
    model = MappedField
    extra=1

class MappableModelAdmin(admin.ModelAdmin):
    form = MappableModelForm
    inlines = [MappedFieldInline]
admin.site.register(MappedModel, MappableModelAdmin)



# class MappedFieldAdmin(admin.ModelAdmin):
#     form = MappedFieldForm
# admin.site.register(MappedField, MappedFieldAdmin)


#admin.site.register(MappedField)


