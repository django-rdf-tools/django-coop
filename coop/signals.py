# -*- coding:utf-8 -*-

from coop.models import StaticURIModel, URI_MODE
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.sites.models import Site
from django.conf import  settings
import rdflib
from rdflib import Graph, ConjunctiveGraph
import subhub
import logging
from urlparse import urlsplit
from django.db.models.loading import get_model
from django.contrib.contenttypes.models import ContentType
import threading
import time
import datetime
import coop_tag
import coop

if getattr(settings, 'SUBHUB_MAINTENANCE_AUTO', False):
    import django_rq


log = logging.getLogger('coop')



class LastDTProcess(object):
    _update = None

    @classmethod
    def get(cls):
        if not cls._update:
            cls._update = datetime.datetime.now() - datetime.timedelta(seconds=2)
        return cls._update - datetime.timedelta(seconds=2)

    @classmethod
    def update(cls):
        now = datetime.datetime.now()
        if not cls._update or now >= cls._update + datetime.timedelta(seconds=10):
            cls._update = now





# Workaround for rqworker limitation
# Be careful, this code is executed by the worker... in its MainThread (I guess
# the worker has a single thread)
# This implies some syncro question.
# For example, if the save is executed from the admin interface, it is
# excuted in its one thread. Thus the DistribustionTask is not created
# when this method is called. Passing the thread name in parameter, we can
# decide in which case we are and then add a small delay to be such that
# admin thread is finished
def letsCallDistributionTaskProcess(thName):
    time.sleep(2)   # wait until thread is finished
    #for dt in subhub.models.DistributionTask.objects.all():
        # log.debug(u'INQUUEU entry_id %s' % dt.entry_id)
    subhub.models.DistributionTask.objects.process(log=log)



# Listener tool
# The point here is to be careful with synchronization.
# subhub.publish will create a new DistributionTask object (if no DistributioTask
# exists for this instance); So the signals will be call again, that why
# the q.enqueue is done only when post_sae_callback is called with a DistributionTask
# as instance.
@receiver(post_save)
def post_save_callback(sender, instance, **kwargs):
    # Initialize the 'sites' many2many field with the default site

    if hasattr(instance, 'sites') and not instance.sites.all().exists():
        instance.sites.add(Site.objects.get_current())

    if hasattr(instance, 'sites') and (
            isinstance(instance, coop.tag.models.CoopTag) or
            # isinstance(instance, coop.tag.models.CoopTaggedItem) or
            isinstance(instance, coop.org.models.BaseContact) or
            isinstance(instance, coop.person.models.BasePerson) or
            isinstance(instance, coop.org.models.BaseRole)):
        for s in Site.objects.all():
            if not s in instance.sites.all():
                instance.sites.add(s)
                instance.save()

    maintenance = getattr(settings, 'SUBHUB_MAINTENANCE_AUTO', False)
    # log.debug(u"Post save callback with sender %s and instance %s and AUTO %s" % (unicode(sender), unicode(instance), maintenance))

    if isinstance(instance, StaticURIModel):
        # if instance.uri_mode == URI_MODE.IMPORTED:
        #     # log.debug(u"%s is imported. Nothing to publish, but subscription renew" % instance)
        #     instance.subscribeToUpdates()
        #     # TODO check if a subscription is done, either lets do it
        # elif isinstance(instance, coop_tag.models.TagBase):
        #     # Subscription done if it does not exists, in other it is simply renew
        #     if hasattr(settings, 'THESAURUS_HOST') and \
        #             not settings.THESAURUS_HOST == 'http://thess.domain.com':
        #         instance.subscribeToUpdates(host=settings.THESAURUS_HOST)
        # else:
        #     domain = Site.objects.get_current().domain
        #     if domain.startswith('http'):
        #         feed_url = '%s/feed/%s/' % (domain, sender.__name__.lower())
        #     else:
        #         feed_url = 'http://%s/feed/%s/' % (domain, sender.__name__.lower())
        #     try:
        #         subhub.publish([feed_url], instance.uri, False)
        #         #log.debug('publish done; Number of Dist task %s' % len(subhub.models.DistributionTask.objects.all()))
        #     except Exception, e:
        #         log.warning(u'Unable to publish %s for feed %s : %s' % (instance, feed_url, e))

        if isinstance(instance, coop.org.models.BaseContact):
            obj = instance.content_object
            if not obj.pref_email and instance.contact_medium_id == 8:
                obj.pref_email = instance
                obj.save()

        if isinstance(instance, coop.org.models.BaseOrganization):
            if instance.pref_phone == None: # bizarre ici il FAUT faire == None et pour pref_mail c'est if not...
                phone_categories = [1, 2]
                fixes = instance.contacts.filter(contact_medium_id__in=phone_categories)
                if fixes.exists():
                    instance.pref_phone = fixes[0]
                    instance.save()
            if not instance.pref_email :
                orgmails = instance.contacts.filter(contact_medium_id=8)
                if orgmails.exists():
                    instance.pref_email = orgmails[0]
                    instance.save()
                elif instance.members.exists():
                    for member in instance.members.all():
                        if member.pref_email:
                            instance.pref_email = member.pref_email
                            instance.save()
                            break
                    


    elif isinstance(instance, subhub.models.DistributionTask) and maintenance:
        try:
            # nb = len(subhub.models.DistributionTask.objects.all())
            #log.debug("before call ENQUEUE, tasks %s" % nb)
            LastDTProcess.update()
            django_rq.enqueue(letsCallDistributionTaskProcess, threading.currentThread().name)
            #log.debug('after call ENQUEUE')
        except Exception, e:
            log.warning(u"%s" % e)
    elif isinstance(instance, subhub.models.SubscriptionTask) and maintenance:
        # call the maintenance
        try:
            log.info(u'Processing verification queue...')
            subhub.models.SubscriptionTask.objects.process(log=log)
        except subhub.utils.LockError, e:
            log.warning(u"%s" % e)
    else:
        pass


# TODO something has to be donne on deleting instance of StaticURIModel
@receiver(post_delete)
def post_delete_callback(sender, instance, **kwargs):
    if isinstance(instance, StaticURIModel):
        if instance.uri_mode == URI_MODE.IMPORTED:
            instance.unsubscribeToUpdates()
        if instance.uri_mode == URI_MODE.LOCAL:
            from coop_local.models import DeletedURI
            #peut etre à completer
            model_name = sender.__name__.lower()
            deleted = DeletedURI(uri=instance.uri, modified=datetime.datetime.now(),\
                rdf_type=unicode(instance.rdf_type), uuid=instance.uuid, model_name=model_name)
            deleted.save()
            domain = Site.objects.get_current().domain
            if domain.startswith('http'):
                feed_url = '%s/feed/%s/' % (domain, sender.__name__.lower())
            else:
                feed_url = 'http://%s/feed/%s/' % (domain, sender.__name__.lower())
            try:
                subhub.publish([feed_url], instance.uri, False)
                #log.debug('publish done; Number of Dist task %s' % len(subhub.models.DistributionTask.objects.all()))
            except Exception, e:
                log.warning(u'Unable to publish %s for feed %s : %s' % (instance, feed_url, e))



def listener(notification, **kwargs):
    ''' Process new content being provided by hub
    '''
    #log.debug("enter listener args %s" % kwargs)
    entry = notification.entries[0]
    uri = str(entry.summary)
    scheme, host, path, query, fragment = urlsplit(uri)
    sp = path.split('/')

   # We have to retreive the instance
    try:
        model = sp[len(sp) - 3]
        mType = ContentType.objects.get(model=model)
        obj = get_model(mType.app_label, model).objects.get(uri=uri)
    except Exception, e:
        obj = None
        log.error(u'%s' % e)

    #  build the rdf graph
    g = Graph()
    if model == 'tag':
        # This is a temporairy work around. thess.economie-solidaire.fr is not
        # yet responding. TODO we have to deal with contexts as tags come thesaurus
        try:
            # TEMP hard coded
            thessEndPoint = 'http://localhost:8080/openrdf-workbench/repositories/thessRepository/query'
            graph = ConjunctiveGraph('SPARQLStore')
            graph.open(thessEndPoint, False)
            ctx = 'http://%s' % str(Site.objects.get_current().domain)
            ctx = rdflib.term.URIRef(ctx)
            localg = graph.get_context(ctx)
        except Exception, e:
            log.error(u'%s' % e)
        gen = localg.triples((rdflib.term.URIRef(uri), None, None))
        try:
            while True:
                g.add(gen.next())
        except:
            pass
        gen = localg.triples((None, None, rdflib.term.URIRef(uri)))
        try:
            while True:
                g.add(gen.next())
        except:
            pass
    else:
        try:
            g.parse(uri)
            #log.debug(u"Handle uri %s" % uri)
        except Exception, e:
            log.error(u"%s" % e)

    # update
    if obj:
        obj.import_rdf_data(g)


