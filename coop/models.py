# -*- coding:utf-8 -*-
from django.db import models
from django.db.models.loading import get_model
from django_extensions.db import fields as exfields
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from extended_choices import Choices
import shortuuid
from rdflib import Graph, plugin, Literal, URIRef, BNode
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from django.db import IntegrityError
from django.template import Template, Context
from urlparse import urlsplit
from django_push.subscriber.models import Subscription
import feedparser
import os
import tempfile
import coop
import datetime
from subhub.models import DistributionTask
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError



URI_MODE = Choices(
    ('LOCAL',  1, _(u'Local')),
    ('COMMON',   2, _(u'Common')),
    ('IMPORTED', 3, _(u'Imported')),
)


# Serializer
plugin.register('n3', plugin.Serializer,
         'rdflib.plugins.serializers.n3', 'N3Serializer')
plugin.register('pretty-xml', plugin.Serializer,
         'rdflib.plugins.serializers.rdfxml', 'PrettyXMLSerializer')
plugin.register('json-ld', plugin.Serializer,
        'rdflib_jsonld.jsonld_serializer', 'JsonLDSerializer')

plugin.register('trix', plugin.Serializer,
                'rdflib.plugins.serializers.trix', 'TriXSerializer')




class TimestampedModel(models.Model):
    created = exfields.CreationDateTimeField(_(u'created'), null=True)
    modified = exfields.ModificationDateTimeField(_(u'modified'), null=True)

    class Meta:
        abstract = True


def get_urimode_from_uri(uri):
    scheme, host, path, query, fragment = urlsplit(uri)
    if host == Site.objects.get_current().domain:
        return URI_MODE.LOCAL
    elif host in ['rdf.insee.fr', 'ns.economie-solidaire.fr', 'data.economie-solidaire.fr']:
        return URI_MODE.COMMON
    else:
        return URI_MODE.IMPORTED


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
    uuid = models.CharField(_(u'uuid'), max_length=50, null=True, editable=False, unique=True, default=shortuuid.uuid)

    links = generic.GenericRelation('coop_local.Link', related_name="%(app_label)s_%(class)s_related")

    # the default value, this attribut should be overloaded
    domain_name = None

    def label(self):
        return "Not Yet Implemented label method"

    # This method could be overwritten by subClasses
    @property
    def uri_id(self):
        if self.uri_mode == URI_MODE.IMPORTED:
            try:
                scheme, host, path, query, fragment = urlsplit(self.uri)
                sp = path.split('/')
                return sp[len(sp) - 2]
            except Exception, e:
                raise ValueError(u'Wrong uri value for %s. Reason %s' % (self.uri, e))
        else:
            return self.uuid

    def uri_registry(self):
        return self.__class__.__name__.lower()

    def init_uri(self):
        return u"http://%s/id/%s/%s/" % (self.domain_name or str(Site.objects.get_current().domain),
                                         self.uri_registry(),
                                         unicode(self.uri_id)  # can be anything = int, uuid, unicode...
                                        )

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
            elif self.uri != self.init_uri():
                # Be careful: we need to keep history of uri modification
                # But it is a little be to early.... uri are link to the domain...
                if getattr(settings, 'URI_FIXED', False):
                    from coop_local.models import LinkProperty, Link
                    self.links.add(Link(predicate=LinkProperty.objects.get(label='replaces'), object_uri=self.uri))
                self.uri = self.init_uri()   # uri_id est pas pareil
        super(StaticURIModel, self).save(*args, **kwargs)




    # try to translate an rdflib object in a django object
    # return None if it fails
    # Bnode are not yet handled.... but it has to be done for the futur
    @staticmethod
    def toDjango(term):
        if isinstance(term, Literal):
            if term.datatype == None:
                return unicode(term)
            else:
                return term.toPython()
        elif isinstance(term, BNode):
            return None
        else:  # let's try to find the django object
            uri = term.toPython()
            scheme, host, path, query, fragment = urlsplit(uri)
            if host == 'rdf.insee.fr':
                # Area de INSEE
                m = models.get_model('coop_geo', 'area')
                try:
                    return m.objects.get(uri=uri)
                except m.DoesNotExist:
                    return None
            elif host == 'ns.economie-solidaire.fr':
                # Exchange Method
                m = models.get_model('coop_local', 'exchangemethod')
                try:
                    return m.objects.get(uri=uri)
                except m.DoesNotExist:
                    return None
            elif host == 'data.economie-solidaire.fr':
                # Role Category
                m = models.get_model('coop_local', 'rolecategory')
                try:
                    return m.objects.get(uri=uri)
                except m.DoesNotExist:
                    pass  # les roles et les tags seront donc traités dans le code qui suit
            # Les normaux ...
            # BIG WARNING : it is supporded that uri dont change and match the model nam
            mName = path.split('/')[2]
            m = models.get_model('coop_local', mName)
            if m == None:
                m = models.get_model('coop_geo', mName)
            if not m == None:
                try:
                    return m.objects.get(uri=uri)
                except m.DoesNotExist:
                    return None
            else:
                return None

    extra_mapping = []

    @property
    def rdf_mapping(self):
        return self.base_mapping + self.extra_mapping

    def base_single_mapping(self, uri, rdfPredicate, djangoField, datatype=None, lang=None):
        value = getattr(self, djangoField)
        if value == None:
            return []
        else:
            rdfSubject = URIRef(uri(self))
            if isinstance(value, models.Model):
                if StaticURIModel in type(value).__mro__:  # or URLField !!!!
                    rdfValue = URIRef(value.uri)
                else:
                    rdfValue = None
            elif isinstance(self._meta.get_field(djangoField), models.URLField):
                rdfValue = URIRef(value)
            else:
                subject_args = {}
                if lang:
                    subject_args['lang'] = lang
                rdfValue = Literal(value, **subject_args)
            if rdfValue == None:
                return []
            else:
                return [(rdfSubject, rdfPredicate, rdfValue)]

    def single_mapping(self, rdfPredicate, djangoField, datatype=None, lang=None):
        uri = lambda x: x.uri
        return self.base_single_mapping(uri, rdfPredicate, djangoField, datatype, lang)


    def local_or_remote_mapping(self, rdfPredicate, djangoField, datatype=None, lang=None):
        uri = lambda x: x.uri
        if getattr(self, djangoField):
            return self.base_single_mapping(uri, rdfPredicate, djangoField, datatype, lang)
        elif hasattr(self, 'remote_' + djangoField + '_uri'):
            if getattr(self, 'remote_' + djangoField + '_uri') == u'':
                return []
            else:
                return self.base_single_mapping(uri, rdfPredicate, 'remote_' + djangoField + '_uri', datatype, lang)
        else:
            return []


    def multi_mapping_base(self, values, rdfPredicate, datatype=None, lang=None):
        rdfSubject = URIRef(self.uri)
        result = []
        subject_args = {}
        if datatype:
            subject_args['datatype'] = datatype
        if lang:
            subject_args['lang'] = lang
        for value in values:
            if URIModel in type(value).__mro__ or 'uri' in value._meta.get_all_field_names():  # et URLField: non on pointe sur des instances de models
                rdfValue = URIRef(value.uri)
            else:
                rdfValue = Literal(unicode(value), **subject_args)
            result.append((rdfSubject, rdfPredicate, rdfValue))
        return result
        # generator ?

    def multi_mapping(self, rdfPredicate, djangoField, datatype=None, lang=None):
        if getattr(self, djangoField) == None:
            return [] 
        else:
            values = getattr(self, djangoField).all()
            return self.multi_mapping_base(values, rdfPredicate, datatype, lang)


    def base_single_reverse(self, uri, g, rdfPred, djField, datatype=None, lang=None, empty_value=None):
        value = list(g.objects(URIRef(uri(self)), rdfPred))
        if len(value) == 1:
            value = value[0]
            if isinstance(self._meta.get_field(djField), models.URLField):
                setattr(self, djField, value.toPython())
            else:
                setattr(self, djField, StaticURIModel.toDjango(value))
        elif len(value) == 0:
            setattr(self, djField, empty_value)
        else:  # plusieurs valeurs ca peut etre une histore de language
            fr_value = []
            for v in value:
                if not v.language == None and v.language == lang:
                    fr_value.append(v)
            if len(fr_value) == 1:
                setattr(self, djField, unicode(fr_value[0]))


    def single_reverse(self, g, rdfPred, djField, datatype=None, lang=None):
        uri = lambda x: x.uri
        self.base_single_reverse(uri, g, rdfPred, djField, datatype, lang)


    def local_or_remote_reverse(self, g, rdfPred, djField, datatype=None, lang=None):
        uri = lambda x: x.uri
        # lets try the local version
        self.base_single_reverse(uri, g, rdfPred, djField, datatype, lang)
        if not getattr(self, djField):
            self.base_single_reverse(uri, g, rdfPred, 'remote_' + djField + '_uri', datatype, lang, empty_value=u'')


    def multi_reverse(self, g, rdfPred, djField, datatype=None, lang=None):
        manager = getattr(self, djField)
        rdf_values = set(g.objects(URIRef(self.uri), rdfPred))
        values = set(map(StaticURIModel.toDjango, rdf_values))
        old_values = set(manager.all())
        remove = old_values.difference(values)
        add = values.difference(old_values)
        for v in remove:
            manager.remove(v)
        for v in add:
            manager.add(v)


    # to be overwriten to filter instance available at rdf level
    def isOpenData(self):
        return True

    def toRdfGraph(self):
        g = Graph()
        if self.rdf_type and self.isOpenData():
            if isinstance(self.rdf_type, list):
                for rt in self.rdf_type:
                    g.add((URIRef(self.uri), settings.NS.rdf.type, rt))
            else:
                g.add((URIRef(self.uri), settings.NS.rdf.type, self.rdf_type))
            for method, arguments, reverse in self.rdf_mapping:
                for triple in getattr(self, method)(*arguments):
                    g.add(triple)
            for l in self.links.all():
                g.add((URIRef(self.uri),  URIRef(l.predicate.uri), URIRef(l.object_uri)))
        return g

    @classmethod
    def get_or_create_from_rdf(cls, uri, graph=None):
        exists = cls.objects.filter(uri=uri).exists()
        if not graph:
            graph = Graph()
            graph.parse(uri)  # RDFLib rules !!!!
        if not exists:
            instance = cls(uri=uri, uri_mode=get_urimode_from_uri(uri))
        else:
            instance = cls.objects.get(uri=uri)
        instance.import_rdf_data(graph)


    def import_rdf_data(self, g):
        for method, arguments, reverse in self.rdf_mapping:
            if hasattr(self, reverse):
                getattr(self, reverse)(g, *arguments)
        from coop_local.models import Link, LinkProperty
         # TODO possible optimisation: Do not remove all links, 
        # check the diffence between new and old values as in previous multi_reverse fonction
        for l in self.links.all():
            self.links.remove(l)
        for lp in LinkProperty.objects.all():
            values = list(g.objects(URIRef(self.uri), URIRef(lp.uri)))
            for v in values:
                link = Link(predicate=lp, object_uri=str(v))
                self.links.add(link)
        self.save()





    # Old version using d2rq
    def toRdf(self, format):
        """
           format correspond to the standard rdflib format keyword,
               'n3' for n3
               'xml' for xml
               'json-ld' for json-ld
               'trix' for trix
        """
        graph = self.toRdfGraph()

        for k in settings.NS:
            graph.bind(k, settings.NS[k])

        if format == 'ttl':
            format = 'n3'
        if format == 'json':
            format = 'json-ld'
        return graph.serialize(format=format)

    def toN3(self):
        return self.toRdf("n3")

    def toXml(self):
        return self.toRdf("xml")

    def toJson(self):
        return self.toRdf("json-ld")

    def toTrix(self):
        return self.toRdf("trig")



    ####
    # TODO
    # The following code has to be cleaned... print, log, ...
    # Still waiting for tests


    @classmethod
    def hostNewUri(cls, old_uri, graph=None):
        """
        This methood change the old_uri, which belong to an external domain_name
        to an uri hosted by this domain. The graph is the rdf graph of the resources.
        The triples are, of course, the following
          <old_uri> <pres1> <value1>
          ....
        but the values are supposed to be up-to-date, we can image that the administrator has change
        (at least checked) them.
        If no graph is provided, old_uri is parsed and used

        This method return the new uri or raise an exception.
        Link between old_uri and new_uri is done with the
        help of the Link model

        We suppose that only model from coop_local could be rehosted.
        """
        if not graph:
            graph = Graph()
            graph.parse(old_uri)

        # check if an instance with thus old_uri exists
        scheme, host, path, query, fragment = urlsplit(old_uri)
        model_name = path.split('/')[2]
        model = get_model('coop_local', model_name)
        if not model:
            raise Exception(_(u"Cannot find a model  for %s" % old_uri))
        try:
            instance = model.objects.get(uri=old_uri)
        except model.DoesNotExist:
            instance = model(uri=old_uri)   # old_uri is still usefull for import_rdf_data

        if instance:
            instance.import_rdf_data(graph)

        from coop_local.models import Link, LinkProperty

        instance.uuid = shortuuid.uuid()
        instance.uri_mode = URI_MODE.LOCAL
        instance.uri = instance.init_uri()
        replaces, created = LinkProperty.objects.get_or_create(uri=settings.NS.dct.replaces, label=u'replaces')
        link = Link(predicate=replaces, object_uri=old_uri)
        instance.links.add(link)
        instance.save()
        return instance.uri


    # La changement d'uri se fait en deux temps : prepareChangeDomainUri et updateDomainUri
    # - on ajoute le triplet olduri dct:isReplacedBy new_uri et on sauve, pour  notifier tous les autres
    # coop qui sont éventuellement abonnéeà cette instance
    # - on met àjour l'uri est le champs uri_mode
    def prepareUpdateDomainUri(self, new_uri):
        """
            When an instance of URIModel asks to rehost its uri to an external domaine. This method
            is called when the new uri has been created by the external domain.
        """
        from coop_local.models import Link, LinkProperty

        replacedBy, created = LinkProperty.objects.get_or_create(uri=settings.NS.dct.isReplacedBy, label=u'isReplacedBy')
        link = Link(predicate=replacedBy, object_uri=new_uri)
        self.links.add(link)
        self.save()

    def updateDomainUri(self, new_uri, sync=False):
        """
        Prerequis : self.prepareChangeDomainUri(new_uri) has been called.
        This means, all other coop which import self.uri are aware of the rehost process, they
        now point to the new_uri object. The instance hasjust to update its uri and uri mode.
        If sync is true, then update is done froom new_uri

        """
        # First check, that all Tasks have been perform. To be such that subcribers are aware of
        # the rehosted action.
        dts = DistributionTask.objects.all()
        if not dts == []:
            DistributionTask.objects.process()
        self.uri = new_uri
        self.uri_mode = URI_MODE.IMPORTED
        if sync:
            g = Graph()
            g.parse(new_uri)
            self.import_rdf_data(g)  # save is done here
        else:
            self.save()      # post_save signal is also doing the new Subcription



    # @classmethod
    # def getD2rqGraph(cls):
    #     context = {}
    #     context['mapping_template'] = 'd2r/' + cls.__name__.lower() + '.ttl'
    #     context['namespaces'] = settings.RDF_NAMESPACES

    #     tmpfile = os.path.dirname(os.path.abspath(coop.__file__)) + '/templates/d2r/model.ttl'
    #     f = open(tmpfile, 'r')
    #     t = Template(f.read())
    #     f.close()
    #     res = t.render(Context(context))
    #     (fd, fname) = tempfile.mkstemp()
    #     f = open(fname, 'w')
    #     f.write(res)
    #     f.close()
    #     graph = Graph()
    #     graph.parse('file:' + fname, format='n3')
    #     return graph

    # @classmethod
    # def updateFromFeeds(cls):
    #     print "Update feed for class name %s" % cls.__name__
    #     feed_url = settings.PES_HOST + 'feed/' + cls.__name__.lower() + '/'
    #     parsedFeed = feedparser.parse(feed_url)
    #     print "Parse feed %s" % feed_url
    #     for entry in parsedFeed.entries:
    #         print "Entry summary is %s " % entry.summary
    #         fd, fname = tempfile.mkstemp()
    #         os.write(fd, entry.summary)
    #         os.close(fd)
    #         g = Graph()
    #         g.parse(fname, format="json-ld")
    #         cls.updateFromGraph(g)


    # @classmethod
    # def updateFromGraph(cls, g):
    #     done = set()
    #     for subj in g.subjects(None, None):
    #         if not (subj in done):
    #             instance = cls.objects.get(uri=str(subj))
    #             if not instance:
    #                 print "Nothing to do with uri %s. Not found in database" % subj
    #             else:
    #                 instance.updateFromRdf(g)
    #             done.add(subj)

    # # Old version with d2R
    # # The "reverse mapping is done here"
    # def updateFromRdf(self, graph):
    #     # Before reversing mapping, we have to check that the uri has not been
    #     # changed. This the case for URI_MODE.IMPORTED instance which still point to
    #     # the old uri

    #     replacedBy = list(graph.objects(URIRef(self.uri), settings.NS.dct.isReplacedBy))
    #     if self.uri_mode == URI_MODE.IMPORTED and len(replacedBy) == 1:
    #         print "Handle rehost imported uri"
    #         g = Graph()
    #         g.parse(replacedBy[0])
    #         self.uri = replacedBy[0]
    #         self.updateFromRdf(g)
    #     else:
    #         db_table = self.__class__._meta.db_table
    #         d2rqGraph = self.__class__.getD2rqGraph()
    #         for field in self._meta.fields:
    #             dbfieldname = db_table + '.' + field.name
    #             pred = checkDirectMap(dbfieldname, d2rqGraph)
    #             if pred:
    #                 update = list(graph.objects(URIRef(self.uri), pred))
    #                 if len(update) > 1:
    #                     print "    The field %s cannot be updated. Too many values" % dbfieldname
    #                 elif len(update) == 0:
    #                     print "Nothing to update for field %s" % dbfieldname
    #                 else:
    #                     print "For id %s update the field %s" % (self.id, dbfieldname)
    #                     update = update[0]
    #                     # Well some field have to be prepared
    #                     if isinstance(field, models.fields.DateField):
    #                         update = update.split('.')[0]
    #                         try:
    #                             tt = time.strptime(update, "%Y-%m-%dT%H:%M:%S")
    #                         except ValueError:
    #                             tt = time.strptime(update, "%Y-%m-%d")
    #                         update = "%d-%d-%d" % (tt.tm_year, tt.tm_mon, tt.tm_mday)
    #                     setattr(self, field.name, update)
    #             elif isinstance(field, models.ForeignKey):
    #                 print "try an FKEY"
    #                 pred = checkDirectMapFK(dbfieldname, d2rqGraph)
    #                 if pred:
    #                     self.updateFKfromRdf(field, dbfieldname, pred, graph)
    #                 else:
    #                     print "    The field %s cannot be updated." % dbfieldname

    #             else:
    #                  # See org/models file to have example of "special" fiels handling
    #                 if hasattr(self, 'updateField_' + field.name):
    #                     getattr(self, 'updateField_' + field.name)(dbfieldname, graph)
    #                 else:
    #                     print "    The field %s cannot be updated." % dbfieldname
    #         print "UpdateFromRdf all fields have been handled"
    #         self.save()
    #         print "save done"


    # def updateFKfromRdf(self, field, dbfieldname, pred, graph):
    #     rdfObj = list(graph.objects(URIRef(self.uri), pred))
    #     if len(rdfObj) == 1:
    #         rdfObj = rdfObj[0]
    #         print "FK object found %s" % rdfObj
    #         if isinstance(rdfObj, URIRef):
    #             try:
    #                 obj = field.related.parent_model.objects.get(uri=str(rdfObj))
    #                 setattr(self, field.name + '_id', obj.id)
    #                 print "For id %s update the field %s" % (self.id, dbfieldname)
    #             except ObjectDoesNotExist:
    #                 # TODO: Object not found in db.... here we have to check il it
    #                 # has to be imported or not.
    #                 print "Obj not in bd : %s" % rdfObj
    #                 print u"    The field %s cannot be updated." % dbfieldname
    #         else:
    #             print "    The field %s cannot be updated." % dbfieldname
    #     else:
    #         print "    The field %s cannot be updated." % dbfieldname

    #     pass


    # This a very simple case, where feed and ub share the same host
    def subscribeToUpdades(self, host=settings.PES_HOST):
        feed_url = "http://%s/feed/%s/%s/" % (host, self.__class__.__name__.lower(), self.uri_id)
        validate = URLValidator(verify_exists=True)
        try:
            subs = Subscription.objects.get(topic=feed_url)
        except Subscription.DoesNotExist:
            subs = None
        if not subs or (subs.lease_expiration and subs.lease_expiration < datetime.datetime.now() + datetime.timedelta(days=10)):   
            try:
                validate(feed_url)
                # print u"Try to subscribe to feed %s" % feed_url
                Subscription.objects.subscribe(feed_url, hub="http://%s/hub/" % host)
            except ValidationError, e:
                print u" Imposible to subscribe to %s : %s" % (feed_url, e)


    def unsubscribeToUpdades(self, host=settings.PES_HOST):
        feed_url = "http://%s/feed/%s/%s/" % (host, self.__class__.__name__.lower(), self.uri_id)
        validate = URLValidator(verify_exists=True)
        try:
            validate(feed_url)
            Subscription.objects.unsubscribe(feed_url, hub="http://%s/hub/" % host)
        except ValidationError, e:
            print u" Imposible to unsubscribe to %s : %s" % (feed_url, e)


class URIModel(StaticURIModel, TimestampedModel):
    class Meta:
        abstract = True


# def checkDirectMap(dbfieldName, d2rqGraph):
#     lit = Literal(dbfieldName)
#     subj = list(d2rqGraph.subjects(settings.NS.d2rq.column, lit))
#     if len(subj) != 1:
#         subj = list(d2rqGraph.subjects(settings.NS.d2rq.uriColumn, lit))
#         if len(subj) != 1:
#             return None
#     subj = subj[0]
#     prop = list(d2rqGraph.objects(subj, settings.NS.d2rq.property))
#     if len(prop) != 1:
#         return None
#     else:
#         return prop[0]


# def checkDirectMapFK(dbfieldName, d2rqGraph):
#     # on commence par chercher tous les triples de la forme
#     # select * where { ?s d2rq:join ?l. filter(?l contains dbfieldname) }
#     # mais comme le d2rqGraph n'est pas un SparqlGraph on le fait à la main

#     # Well it is not possible to use settings.NS.d2rq.join because
#     # there is a conflict of names with the join function of the Namespace
#     # class....
#     tr = list(d2rqGraph.triples((None, URIRef(str(settings.NS.d2rq) + 'join'), None)))

#     def useField((s, p, o)):
#         if isinstance(o, Literal):
#             return dbfieldName in o
#         else:
#             return False
#     candidate = filter(useField, tr)
#     if len(candidate) == 1:
#         print "Found candidate"
#         subj = candidate[0][0]
#         prop = list(d2rqGraph.objects(subj, settings.NS.d2rq.property))
#         if len(prop) == 1:
#             return prop[0]
#         else:
#             return None
#     else:
#         return None



def rdfGraphAll(model=None):
    """
    """
    g = Graph()
    for k in settings.NS:
        g.bind(k, settings.NS[k])

    if model == None:
        for m in models.get_models():
            if coop.models.StaticURIModel in m.__mro__:
                for o in m.objects.all():
                    g += o.toRdfGraph()
    else:
        m = models.get_model('coop_local', model)
        if m == None:
            m = models.get_model('coop_geo', model)
        if m == None:
            print _(u"Warning")
            print _(u"Warning no model found for model name %s" % model)
        else:
            for o in m.objects.all():
                g += o.toRdfGraph()
    return g


def rdfDumpAll(destination, format, model=None):
    g = rdfGraphAll(model)
    g.serialize(destination, format=format)


# It seems to be the best place to do the connection
# see http://stackoverflow.com/questions/7115097/the-right-place-to-keep-my-signals-py-files-in-django
# from django.core.signals import  request_finished
from coop.signals import listener
from django_push.subscriber.signals import updated

# request_finished.connect(post_save_callback, sender=StaticURIModel)
# request_finished.connect(post_delete_callback, sender=StaticURIModel)
updated.connect(listener)




