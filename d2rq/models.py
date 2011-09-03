# -*- coding:utf-8 -*-
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _
import surf, rdflib
from surf import ns
from surf.query import select,a
from urllib2 import Request, urlopen, URLError, HTTPError
#from djutils.decorators import async
import settings
import re
import os.path

def literal_lang_select(list):
    '''
    Ou 'list' est une liste de rdflib.term.literal 
    '''
    result = None
    pref_lang = 'fr' #TODO livesettings
    fallback = 'en'
    for literal in list:
        if(literal.language == pref_lang):
            result = unicode(literal)
            break
        elif(literal.language == fallback):
            result = unicode(literal)
        elif(not result):
            result = unicode(literal)
    return(' '.join(result.split()))        


#@async    
def download_schema(uri, prefix):
    headers = { "Accept": "text/turtle,text/n3,text/rdf+n3,application/rdf+xml,text/rdf,text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5",
                "Accept-Language": "en-us,en;q=0.5",
                "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
                "User-Agent": "django-d2rq"
                }
    req = Request(uri,None,headers)
    try:
        handle = urlopen(req)
    except URLError, e:
        print 'La connexion avec le serveur a échoué.'
        print 'Raison: ', e.reason
    except HTTPError, e:
        print 'Erreur du serveur.'
        print 'Code : ', e.code
    format = handle.info().gettype()
    formats = { 'application/rdf+xml':'rdf','text/turtle' : 'ttl',
                'text/n3' :'n3','text/rdf+n3':'n3','text/rdf':'rdf',
                'text/xml':'xml','application/xml':'xml'}
    extension = formats[format]
    filename = 'd2rq/vocab/'+prefix+'.'+extension
    local_file = open(filename, "w")
    local_file.write(handle.read())
    local_file.close()
    return extension


def get_label(subject,baseuri,store):
    label = None
    ns_titles = [ns.RDFS["comment"],ns.RDFS["label"],ns.DC["title"],ns.DCTERMS["title"]]
    for title in ns_titles:
        query = select("?o").where((subject,title,"?o"))
        found_title = list(store.reader._to_table(store.reader._execute(query)))
        #print 'Nombre de labels '+title+' :'+str(len(found_title))
        if(len(found_title)>0):
            label = literal_lang_select([found_title[x]['o'] for x in range(len(found_title))])
    if(label==None): #on n'a rien trouvé du tout
        label = unicode(subject).replace(baseuri,'')
    return label    


def get_schema_label(uri,prefix,format):
    #store = surf.Store(reader='rdflib',writer='rdflib',rdflib_store='IOMemory')
    store = surf.Store(**{"reader": "librdf", "writer" : "librdf", })
    session = surf.Session(store)
    try:
        store.load_triples(source='file://'+settings.PROJECT_PATH+'/d2rq/vocab/'+prefix+'.'+format)
        print "Loading from file : "+prefix+"."+format
    except:
        store.load_triples(source=uri)
        print "Loading from Internet : "+uri
    #store.enable_logging(True)
    ontology = session.get_class(ns.OWL.Ontology)
    if(ontology.all().first()): #contient un node Ontology
        print "Le schema est une ontologie OWL"
        vocab_type = 'owl'
        titles = ['rdfs_comment','rdfs_label','dc_title','dcterms_title']
        #import pdb; pdb.set_trace() 
        for o in ontology.all():
            for title in titles:
                if(len(o.__getattr__(title))>0):
                    lookup = literal_lang_select(o.__getattr__(title))
                    if(lookup != None):label=lookup
            if not label:
                label = unicode(uri)
    else: # là c'est la vraie methode, 
    #au-dessus c'est juste pour les OWL dont l'URL ≠ de l'URI sujet
    #donc pas forcément obligatoire à garder non plus
        try:
            print "Le schema est un vocabulaire RDFS"
            vocab_type = 'rdfs'
            label = get_label(rdflib.term.URIRef(uri),uri,store)
        except:
            raise
    lookup_args = { 'owl':  (ns.OWL.Class,ns.OWL.ObjectProperty),
                    'rdfs': (ns.RDFS.Class,ns.RDF.Property)}
    vocab_classes = list(store.reader._to_table(store.reader._execute(
                        select("?s").where(("?s", a, lookup_args[vocab_type][0])).filter('(regex(str(?s),"'+uri+'","i"))')# vocab own classes only
                        )))
    vocab_proprietes = list(store.reader._to_table(store.reader._execute(
                        select("?s").where(("?s", a, lookup_args[vocab_type][1])).filter('(regex(str(?s),"'+uri+'","i"))')
                        )))   
    cp = {'classes':[],'proprietes':[]}                        
    for items in ((vocab_classes,'classes'),(vocab_proprietes,'proprietes')):
        for triple in items[0]:
            if(isinstance(triple['s'],rdflib.term.URIRef) and bool(re.compile(uri).match(unicode(triple['s'])))): #ugly patch waiting for query to work
                clabel = get_label(triple['s'],uri,store) #on envoie le subject pour l'identifier
                cp[items[1]].append((unicode(triple['s']),clabel))
                print items[1]+':'+clabel
    store.clear()
    store.close()
    session.close()
    return((label,vocab_type,cp))


def update_class_and_properties(schema):
    pass



class SchemaManager(models.Manager):
    def get_by_natural_key(self, prefix, uri):
        return self.get(prefix=prefix, uri=uri)

class Schema(models.Model):
    objects = SchemaManager()
    prefix = models.CharField(_(u'Préfixe du schéma'),max_length=10)
    uri = models.CharField(_(u'URI du schéma'),max_length=200) #TODO URIField that does not cut "#" at the end would be cool
    label = models.CharField(_(u'Intitulé'),max_length=200,blank=True,editable=False)
    format = models.CharField(blank=True, max_length=5,editable=False)
    vocab_type = models.CharField(blank=True, max_length=5,editable=False)
    def natural_key(self):
        return (self.prefix, self.uri)
    class Meta:
        ordering = ('prefix',)
        unique_together =(('prefix','uri'),)
    def __unicode__(self):
        return unicode(self.label)
    def link_in_admin(self):
        return '<a target="_blank" href="%s">%s</a>' % (self.uri, self.uri)
    link_in_admin.allow_tags = True   
    def save(self, *args, **kwargs): 
        print 'Ajout/mise à jour de '+str(self.uri)     
        if(os.path.exists(settings.PROJECT_PATH+'/d2rq/vocab/'+self.prefix+'.'+self.format)):
            print 'Utilisation de la copie locale'
        else:        
            self.format = download_schema(self.uri,self.prefix)
            print 'Téléchargement du fichier'
        print 'Serialisation du schema : '+self.format
        #exception : pas téléchargeable
        if(self.format in ['rdf','n3','ttl']):
            try:
                self.label, self.vocab_type,cp = get_schema_label(self.uri,self.prefix,self.format)
                print 'Titre : "'+self.label+'", Type de schema : '+self.vocab_type
            except:
                raise
        else:
            self.label = self.uri
            self.vocab_type = '???'   
        super(Schema, self).save(*args, **kwargs)
        # update_class_and_properties(self)
        if('cp' in locals()):
            SchemaClass.objects.filter(schema=self).delete()
            SchemaProperty.objects.filter(schema=self).delete()
            for sc in cp['classes']:
                sc = SchemaClass(schema=self,class_name=sc[0],class_label=sc[1])
                sc.save()
            for sp in cp['proprietes']:
                sp = SchemaProperty(schema=self,prop_name=sp[0],prop_label=sp[1])
                sp.save()

from utils import FkFilterSpec
FkFilterSpec.register_filterspec()

# def get_rdf_classes():              
#     AVAILABLE_CLASSES = []
#     for s in Schema.objects.all().order_by('prefix'):
#         AVAILABLE_CLASSES.append((
#             s.prefix+':', 
#             tuple((x.id,x.class_label) for x in SchemaClass.objects.filter(schema=s))
#         ))
#     return AVAILABLE_CLASSES


class SchemaClass(models.Model):
    schema = models.ForeignKey(Schema)
    class_name = models.CharField(_(u'Classe RDF'),max_length=250,unique=True)
    class_label = models.CharField(_(u'Libellé'),max_length=250)

    def __unicode__(self):
        return(self.class_label)    
    class Meta:
        #unique_together = (('class_name', 'class_label'),)
        ordering = ('class_label',)
        verbose_name = _(u'Classe RDF')
        verbose_name_plural = _(u'Classes RDF')


class SchemaProperty(models.Model):
    schema = models.ForeignKey(Schema)
    prop_name = models.CharField(_(u'Propriété RDF'),max_length=250,unique=True)
    prop_label = models.CharField(_(u'Libellé'),max_length=250)
    def __unicode__(self):
        return(self.prop_label)
    class Meta:
        #unique_together = (('prop_name', 'prop_label'),)
        ordering = ('prop_label',)
        verbose_name = _(u'Propriété RDF')
        verbose_name_plural = _(u'Propriétés RDF')        


from smart_selects.db_fields import ChainedForeignKey

class MappedModel(models.Model):
    model_name = models.ForeignKey(ContentType,verbose_name=_(u'Modéle mappé'))
    schema = models.ForeignKey(Schema)
    rdf_class = ChainedForeignKey(SchemaClass,
                    chained_field='schema',
                    chained_model_field='schema',
                    show_all=False,
                    verbose_name=_(u'Classe RDF'))
    
    #rdf_class = models.ForeignKey(SchemaClass,verbose_name=_(u'Classe RDF')) 
    classMap_label = exfields.AutoSlugField('d2rq:classDefinitionLabel',populate_from=('rdf_class'))
    class Meta:
        verbose_name = _(u'Modèle mappé')
        verbose_name_plural = _(u'Modèles mappés')
    def __unicode__(self):
        return(unicode(self.model_name.app_label)+u'.'+unicode(self.model_name)+u' ➔ '+
                unicode(self.rdf_class.schema.prefix)+u':'+unicode(self.rdf_class))


class MappedField(models.Model):
    model = models.ForeignKey(MappedModel,verbose_name=_(u'Mapping'))
    field_name = models.CharField(max_length=250)
    schema = models.ForeignKey(Schema)
    rdf_property = ChainedForeignKey(SchemaProperty,
                    chained_field='schema',
                    chained_model_field='schema',
                    show_all=False,
                    verbose_name=_(u'Propriété RDF'))
    #rdf_property = models.ForeignKey(SchemaProperty,verbose_name=_(u'Propriété RDF'),null=True)
    # PropertyDef_label = exfields.AutoSlugField('d2rq:propertyDefinitionLabel',populate_from=('rdf_property'))
    # def __unicode__(self):
    #     return(unicode(self.model.model_name.app_label)+u'.'+unicode(self.model_name)+u' ➔ '+
    #             unicode(self.rdf_class.schema.prefix)+u':'+unicode(self.rdf_class))
    class Meta:
        verbose_name = _(u'Champ mappé')
        verbose_name_plural = _(u'Champs mappés')