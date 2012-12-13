# -*- coding:utf-8 -*-
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rdflib import Graph, URIRef, Literal
import logging

log = logging.getLogger('coop')




class DeletedURI(models.Model):
    uri = models.CharField(blank=True, unique=True, max_length=250, editable=False)
    modified = models.DateTimeField()
    rdf_type = models.CharField(blank=True, max_length=250, editable=False)
    uuid = models.CharField(max_length=50, null=True, editable=False, unique=True)
    model_name = models.CharField(max_length=50, editable=False)


    def __unicode__(self):
        return u'DeletedURI <%s>' % self.uri

    def label(self):
        return unicode(self)

    class Meta:
        abstract = True
        app_label = 'coop_local'

    def toRdf(self, format):
        """
           format correspond to the standard rdflib format keyword,
               'n3' for n3
               'xml' for xml
               'json-ld' for json-ld
               'trix' for trix
        """
        graph = Graph()
        for k in settings.NS:
            graph.bind(k, settings.NS[k])

        graph.add((URIRef(self.uri), settings.NS.rdf.type, URIRef(self.rdf_type)))
        graph.add((URIRef(self.uri), settings.NS.ov.deletedOn, Literal(self.modified)))
        if format == 'ttl':
            format = 'n3'
        if format == 'json':
            format = 'json-ld'
        return graph.serialize(format=format)
