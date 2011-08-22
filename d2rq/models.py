# -*- coding:utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _


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
        elif(not result and not lit.language):
            result = unicode(lit)
    return(result)        
            

def get_schema_label(uri):
    import surf
    store = surf.Store(reader='rdflib',writer='rdflib',rdflib_store='IOMemory')
    session = surf.Session(store)
    store.load_triples(source=uri)
    #store.enable_logging(True)
    ontology = session.get_class(surf.ns.OWL.Ontology)
    #vocab = session.get_class(surf.ns.RDF.Description)
    if(ontology.all().first()): metablock = ontology #une ontologie OWL
    #elif(vocab.all().first()):  metablock = vocab #un vocabulaire RDF ... comment faire ?
    else:label = unicode(uri)   # Schéma non reconnu on prend l'URI comme titre
    if(metablock): #pourrait partir ailleurs
        titles = ['rdfs_comment','rdfs_label','dc_title','dcterms_title'] 
        # du moins évident vers le plus évident, pas terrible
        # faudrait évaluer chaque cas et décider ensuite plutot que d'ecraser
        for o in metablock.all():
            for title in titles:
                print title,':',o.__getattr__(title)
                lookup = literal_lang_select(o.__getattr__(title))
                if(lookup != None):label=lookup
            if(not label):
                label = unicode(o.subject)
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
    modelname = models.TextField(_(u'Modéle mappé'))

class MappedField(models.Model):
    model = models.ForeignKey(MappedModel)
    fieldname = models.TextField(_(u'Champ mappé'))
    class_prop = models.TextField(_(u'Classe ou propriété RDF'),blank=True)