# -*- coding:utf-8 -*-
from django.db import models
from django_extensions.db import fields as exfields
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from extended_choices import Choices
import shortuuid
from rdflib import Graph, plugin, store, Literal, URIRef
from django.db import IntegrityError
from django.template import Template, Context
from urlparse import urlsplit
import feedparser
import os
import tempfile
import coop
import time




URI_MODE = Choices(
    ('LOCAL',  1, _(u'Local')),
    ('COMMON',   2, _(u'Common')),
    ('IMPORTED', 3, _(u'Imported')),
)

# Store
plugin.register('SPARQLStore', store.Store,
        'rdflib_sparqlstore.SPARQLStore', 'SPARQLStore')

# Serializer
plugin.register('n3', plugin.Serializer,
         'rdflib.plugins.serializers.n3', 'N3Serializer')
plugin.register('pretty-xml', plugin.Serializer,
         'rdflib.plugins.serializers.rdfxml', 'PrettyXMLSerializer')
plugin.register('json-ld', plugin.Serializer,
        'rdflib_jsonld.jsonld_serializer', 'JsonLDSerializer')


class TimestampedModel(models.Model):
    created = exfields.CreationDateTimeField(_(u'created'), null=True)
    modified = exfields.ModificationDateTimeField(_(u'modified'), null=True)

    class Meta:
        abstract = True


class StaticURIModel(models.Model):
    """
    To use this model as a basis for your own abstract model, you need to have
    a 'uri_id' property set and a string for the model type URL representation :

    @property
    def uri_id(self):
        return self.username # example with username

    uri_registry = 'org'

    the uri_fragment can then be overriden in a real model derived from your abstract model

    """
    class Meta:
        abstract = True

    uri_mode = models.PositiveSmallIntegerField(_(u'Mode'), choices=URI_MODE.CHOICES, default=URI_MODE.LOCAL, editable=False)
    uri = models.CharField(_(u'main URI'), blank=True, null=True,
                            max_length=250, editable=False)  # FIXME : null=True incompatible with unique=True

    # Le code suivante ne marche pas avec south et pourtant il correxpond exactement à ce que je voudrais
    # faire. Si on supprime unique=True, alors la migration se passe bien, mais toutes les
    # du model ont la meme valeur.... Et bien sur, si on met uniaue=True, south rale car
    # le champs n'est pas unique.
    # South n'a pas l'air capable de traiter ce cas.
    # D'apres la doc, il est possible de le faire en 3 fois, sans utiliser le default, avec
    # un datamigration (voir la doc Part 3: Advanced Commands and Data Migrations)
    #uuid = models.CharField(_(u'uuid'), max_length=50, default=shortuuid.uuid, unique=True)

    # La version simple c'est de passer par le save() et de supprimer le default.... c'est pas
    # tres beau, car un plus couteux en runtime... mais bon
    uuid = models.CharField(_(u'uuid'), max_length=50, unique=True, null=True, default=shortuuid.uuid, editable=False)

    # the default value, this attribut should be overloaded
    domain_name = settings.DEFAULT_URI_DOMAIN
    #str(Site.objects.get_current().domain)

    def label(self):
        return "NYI label method"

    # This metho could be overwritten by subClasses
    @property
    def uri_id(self):
        return self.uuid

    def uri_registry(self):
        return self.__class__.__name__.lower()

    def init_uri(self):
        return 'http://' + self.domain_name + '/id/' + self.uri_registry() + '/' + str(self.uri_id) + '/'




    # self.uri est null ou vide le creer (cad appel init_uri)
    # si le domain a changé alors changer l'uri (cad dire appel init_uri)
    # si le uri_registery a changer alors changer l'uri
    # attention dans les 2 cas le uuid ne bouge pas.... il faut alors aller le chercher
    #
    # repenser aux commons et aux importés pour voir si tout marche



    def save(self, *args, **kwargs):
         # create / update URI
        if self.uri_mode != URI_MODE.IMPORTED:
            if not self.uri or self.uri == '':
                self.uri = self.init_uri()
            else:
                scheme, host, path, query, fragment = urlsplit(self.uri)
                sp = path.split('/')
                try:
                    assert(sp[1] == 'id')  # to assert a minimal coherence...
                except AssertionError:
                    raise IntegrityError(_(u'Local URI path must starts with "/id/"'))
                if sp[3] != self.uri_id:
                    self.uri = self.init_uri()  # uri_id est pas pareil
                else:
                    if host != self.domain_name:
                        self.uri = self.init_uri()
                    else:
                        if  sp[2] != self.uri_registry():
                            self.uri = self.init_uri()
        super(StaticURIModel, self).save(*args, **kwargs)



    def toRdf(self, format):
        """
           format correspond to the standard rdflib format keyword,
               'n3' for n3
               'xml' for xml
               'json-ld' for json-ld
        """
        # Sparq endPoint
        uriSparql = 'http://localhost:8080/' + settings.PROJECT_NAME + '/sparql'
        graph = Graph(store="SPARQLStore")
        graph.open(uriSparql, False)
        graph.store.baseURI = str(uriSparql)

        # The short form of the construct where see 16.2.4 CONSTRUCT WHERE http://www.w3.org/TR/sparql11-query/#constructWhere
        cquery = "construct where { <%s> ?p ?o .} "
        res = graph.query(cquery % self.uri)
        filename = "/tmp/%stmp.rdf" % self.uuid
        tmpfile = open(filename, "w")
        res.serialize().write(tmpfile, encoding='utf-8')
        tmpfile.close()
        g = Graph()
        for p, ns in settings.RDF_NAMESPACES.iteritems():
            g.bind(p, ns)
        g.parse(filename)

        if format == 'ttl': format = 'n3'
        if format == 'json': format = 'json-ld'

        return g.serialize(format=format)

    def toN3(self):
        return self.toRdf("n3")

    def toXml(self):
        return self.toRdf("xml")

    def toJson(self):
        return self.toRdf("json-ld")


    @classmethod
    def getD2rqGraph(cls):
        context = {}
        context['mapping_template'] = 'd2r/' + cls.__name__.lower() + '.ttl'
        context['namespaces'] = settings.RDF_NAMESPACES

        tmpfile = os.path.dirname(os.path.abspath(coop.__file__)) + '/templates/d2r/model.ttl'
        f = open(tmpfile, 'r')
        t = Template(f.read())
        f.close()
        res = t.render(Context(context))
        (fd, fname) = tempfile.mkstemp()
        f = open(fname, 'w')
        f.write(res)
        f.close()
        graph = Graph()
        graph.parse('file:' + fname, format='n3')
        return graph




    @classmethod
    def updateFromFeeds(cls):
        print "Update feed for class name %s" % cls.__name__
        feed_url = settings.PES_HOST + 'feed/' + cls.__name__.lower() + '/'
        parsedFeed = feedparser.parse(feed_url)
        print "Parse feed %s" % feed_url
        for entry in parsedFeed.entries:
            print "Entry summary is %s " % entry.summary
            fd, fname = tempfile.mkstemp()
            os.write(fd, entry.summary)
            os.close(fd)
            g = Graph()
            g.parse(fname, format="json-ld")
            done = set()
            for subj in g.subjects(None, None):
                if not (subj in done):
                    instance = cls.objects.get(uri=str(subj))
                    if not instance:
                        print "Nothing to do with uri %s. Not found in database" % subj
                    else:
                        instance.updateFromRdf(g)
                    done.add(subj)

    # The "reverse mapping is done here"
    def updateFromRdf(self, graph):
        db_table = self.__class__._meta.db_table
        d2rqGraph = self.__class__.getD2rqGraph()
        for field in self.__class__._meta.fields:
            dbfieldname = db_table + '.' + field.name
            pred = checkDirectMap(dbfieldname, d2rqGraph)
            if pred:
                update = list(graph.objects(URIRef(self.uri), pred))
                if len(update) > 1:
                    print "    The field %s cannot be updated. Too many values" % dbfieldname
                elif len(update) == 0:
                    print "Nothing to update for field %s" % dbfieldname
                else:
                    print "For id %s update the field %s" % (self.id, dbfieldname)
                    update = update[0]
                    # Well some field have to be prepared
                    if isinstance(field, models.fields.DateField):
                        update = update.split('.')[0]
                        tt = time.strptime(update, "%Y-%m-%dT%H:%M:%S")
                        update = "%d-%d-%d" % (tt.tm_year, tt.tm_mon, tt.tm_mday)
                    setattr(self, field.name, update)
            else:
                 # See org/models file to have example of "special" fiels handling
                if hasattr(self, 'updateField_' + field.name):
                    getattr(self, 'updateField_' + field.name)(dbfieldname, graph)
                else:
                    print "    The field %s cannot be updated." % dbfieldname
        self.save()




class URIModel(StaticURIModel, TimestampedModel):
    class Meta:
        abstract = True






def checkDirectMap(dbfieldName, d2rqGraph):
    lit = Literal(dbfieldName)
    subj = list(d2rqGraph.subjects(settings.NS_D2RQ.column, lit))
    if len(subj) != 1:
        subj = list(d2rqGraph.subjects(settings.NS_D2RQ.uriColumn, lit))
        if len(subj) != 1:
            return None
    subj = subj[0]
    prop = list(d2rqGraph.objects(subj, settings.NS_D2RQ.property))
    if len(prop) != 1:
        return None
    else:
        return prop[0]


# It seems to be the best place to do the connection
# see http://stackoverflow.com/questions/7115097/the-right-place-to-keep-my-signals-py-files-in-django
from django.core.signals import  request_finished
from coop.signals import post_save_callback
request_finished.connect(post_save_callback, sender=StaticURIModel)
