#-*- coding:utf-8 -*-
from django.contrib import admin
from skosxl.models import *


class TermInline(admin.TabularInline):
    model = Term.concept.through
    extra=1
    
class SimilarInline(admin.TabularInline):
    model = SimilarConcept
    extra=1    

class ConceptAdmin(admin.ModelAdmin):
    inlines = [
            TermInline,SimilarInline
        ]

class TermAdmin(admin.ModelAdmin):
    list_display = ('literal','created')
    search_fields = ['literal','slug']
   
admin.site.register(Term, TermAdmin)

admin.site.register(Concept, ConceptAdmin)
admin.site.register(Vocabulary)
