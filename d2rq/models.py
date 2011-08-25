# -*- coding:utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

import surf, rdflib
from surf.query import *

def literal_lang_select(list):
    '''
    Ou 'list' est une liste de rdflib.term.literal 
    '''
    result = None
    pref_lang = 'fr' #TODO livesettings
    fallback = 'en'
    for lit in list:
        if(lit.language == pref_lang):
            result = unicode(lit)
            break
        elif(lit.language == fallback):
            result = unicode(lit)
        elif(not result):
            result = unicode(lit)
    return(result)        


def get_schema_label(uri):

    #store = surf.Store(reader='rdflib',writer='rdflib',rdflib_store='IOMemory')
    store = surf.Store(**{"reader": "librdf", "writer" : "librdf", })
    session = surf.Session(store)
    store.load_triples(source=uri)
    #store.enable_logging(True)
    ownuri = rdflib.term.URIRef(uri)
    ontology = session.get_class(surf.ns.OWL.Ontology)
    if(ontology.all().first()): #contient un node Ontology
        titles = ['rdfs_label','dc_title','dcterms_title']
        for o in ontology.all():
            for title in titles:
                lookup = literal_lang_select(o.__getattr__(title))
                if(lookup != None):label=lookup
            if(not label):
                label = unicode(uri)
    else: #ce n'est pas une ontologie OWL, idem mais autre méthode , orientée query
    # cette méthode pourrait fonctionner pour les ontologies aussi, sauf quand
    #(pb 303 ou autre) l'URI sujet est differente de l'URI stockée...
    
        ns_titles = [surf.ns.RDFS["label"],surf.ns.DC["title"],surf.ns.DCTERMS["title"]]
        for title in ns_titles:
            query = select("?o").where((ownuri,title,"?o"))
            found_title = list(store.reader._to_table(store.reader._execute(query)))

            if(len(found_title)==1):
                label = literal_lang_select([found_title[0]['o']])
        if(not label): #on n'a rien trouvé avec la méthode vocab
            label = unicode(uri)
    #import pdb; pdb.set_trace()                
    store.clear()
    store.close()
    session.close()
    print label
    return(label)
    
class Schema(models.Model):
    prefix = models.CharField(_(u'Préfixe du schéma'),max_length=10)
    uri = models.CharField(_(u'URI du schéma'),max_length=200) #URIField that does not cut "#" at the end would be cool
    label = models.CharField(_(u'Intitulé'),max_length=200,blank=True,editable=False)
    def __unicode__(self):
        return unicode(self.label)
    def link_in_admin(self):
        return '<a target="_blank" href="%s">%s</a>' % (self.uri, self.uri)
    link_in_admin.allow_tags = True
        
    def save(self, *args, **kwargs):
        try:
            self.label = get_schema_label(self.uri)
        except:
            self.label = self.uri           
        super(Schema, self).save(*args, **kwargs)

class MappedModel(models.Model):
    modelname = models.CharField(_(u'Modéle mappé'),choices=selected_models)

class MappedField(models.Model):
    model = models.ForeignKey(MappedModel)
    fieldname = models.TextField(_(u'Champ mappé'))
    class_prop = models.TextField(_(u'Classe ou propriété RDF'),blank=True)
    