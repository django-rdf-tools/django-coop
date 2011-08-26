# -*- coding:utf-8 -*-
from django.contrib import admin
from d2rq.models import Schema,MappedModel,MappedField
from django import forms

class SchemaAdmin(admin.ModelAdmin):
    list_display = ('prefix','label','link_in_admin',)
    list_display_links =('prefix','label')
    ordering = ('prefix',)
admin.site.register(Schema,SchemaAdmin)

admin.site.register(MappedModel)


class OntologySelectWidget(forms.Select):
    pass

def ontology_get_list(uri,prefix):
    import surf,rdflib
    liste = []
    try:
        store = surf.Store(**{"reader": "librdf", "writer" : "librdf"})
        #store = surf.Store(reader='rdflib',writer='rdflib',rdflib_store='IOMemory')
        session = surf.Session(store)
        store.load_triples(source=uri)
        #ontology = session.get_class(surf.ns.OWL.Ontology)
        #o = ontology("http://www.w3.org/ns/org#")
        #unicode(o.rdfs_label.first)
        classes = session.get_class(surf.ns.RDFS.Class)
        print classes
        proprietes = session.get_class(surf.ns.RDF.Property)
        subclasses = session.get_class(surf.ns.RDFS.subClassOf)
        for c in classes.all():
            if(isinstance(c.subject,rdflib.term.URIRef)):
                option = (c.subject.replace(uri,prefix+':'),u'[C] '+unicode(c.rdfs_label.first))
                liste.append(option)
        for p in proprietes.all():
            if(isinstance(c.subject,rdflib.term.URIRef)):
                option = (c.subject.replace(uri,prefix+':'),u'[P] '+unicode(c.rdfs_label.first))
                liste.append(option)        
        session.close()
        store.close()        
    except Exception,e:
        print e
    return tuple(liste)


class ClassPropAdminForm(forms.ModelForm):
    class Meta:
        model = MappedField
    def __init__(self,*args,**kwargs):
        super(ClassPropAdminForm, self).__init__(*args,**kwargs)
        #qs = MyModel.objects.exclude(pk = self.instance.pk) #grab instance.pk here
        self.widgets = {
            'class_prop' : OntologySelectWidget(choices=ontology_get_list(self.instance.uri,self.instance.prefix),)
        }



