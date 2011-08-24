#-*- coding:utf-8 -*-
from django.contrib import admin
from skosxl.models import *

admin.site.register(Term)

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
    
admin.site.register(Concept, ConceptAdmin)
admin.site.register(Vocabulary)
