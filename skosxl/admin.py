#-*- coding:utf-8 -*-
from django.contrib import admin
from skosxl.models import *
from django.utils.translation import ugettext_lazy as _

from coop.autocomplete_admin import FkAutocompleteAdmin,InlineAutocompleteAdmin

class TermInline(InlineAutocompleteAdmin):
    model = Term.concept.through
    fields = ('type','term',)
    related_search_fields = {'term' : ('literal',)}
    #readonly_fields = ('term',)
    extra=1
    
class SKOSMappingInline(admin.TabularInline):
    model = MapRelation
    fields = ('voc','target_label','match_type',)
    readonly_fields = ('target_label','uri')
    extra=1    

class RelAdmin(InlineAutocompleteAdmin):
    model = SemRelation
    fk_name = 'origin_concept'
    fields = ('type', 'target_concept')
    related_search_fields = {'target_concept' : ('labels__term__literal','definition')}#c.labels.all()[0].term.literal
    extra = 1

class ConceptAdmin(FkAutocompleteAdmin):
    readonly_fields = ('author','created','modified')
    change_form_template = 'admin_concept_change.html'
    fieldsets = (   (_(u'Meta-data'),
                    {'fields':(('definition','changenote'),'author','created','modified'),
                     'classes':('collapse',)}),
                    
                     
                     )
    inlines = [  TermInline, RelAdmin, SKOSMappingInline ]

class TermAdmin(admin.ModelAdmin):
    list_display = ('literal','created')
    search_fields = ['literal','slug']
   
admin.site.register(Term, TermAdmin)

admin.site.register(Concept, ConceptAdmin)
admin.site.register(Vocabulary)
