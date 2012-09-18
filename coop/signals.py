# -*- coding:utf-8 -*-

from coop.models import StaticURIModel, URI_MODE
from django.db.models.signals import post_save, post_delete
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

if getattr(settings, 'SUBHUB_MAINTENANCE_AUTO', False):
    import django_rq


log = logging.getLogger('subhub.maintenance')



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
    if not thName == threading.currentThread().name:
        time.sleep(2)   # wait until thread is finished
    for dt in subhub.models.DistributionTask.objects.all():
        print log.debug(u'INQUUEU entry_id %s' % dt.entry_id)
    subhub.models.DistributionTask.objects.process(log=log)


# Listener tool
# The point here is to be careful with synchronization.
# subhub.publish will create a new DistributionTask object (if no DistributioTask
# exists for this instance); So the signals will be call again, that why
# the q.enqueue is done only when post_sae_callback is called with a DistributionTask
# as instance.
@receiver(post_save)
def post_save_callback(sender, instance, **kwargs):
    maintenance = getattr(settings, 'SUBHUB_MAINTENANCE_AUTO', False)
    log.debug(u"Post save callback with sender %s and instance %s and AUTO %s" % (sender, instance, maintenance))

    if isinstance(instance, StaticURIModel):
        if instance.uri_mode == URI_MODE.IMPORTED:
            log.debug(u"%s is imported. Nothing to publish, but subscription renew" % instance)
            instance.subscribeToUpdades()
            # TODO check if a subscription is done, either lets do it
        elif isinstance(instance, coop_tag.models.TagBase):
            # Subscription done if it does not exists, in other it is simply renew
            instance.subscribeToUpdades(host=settings.THESAURUS_HOST)
        else:
            feed_url = 'http://%s/feed/%s/' % (Site.objects.get_current().domain, sender.__name__.lower())
            try:
                subhub.publish([feed_url], instance.uri, False)
                log.debug('publish done; Number of Dist task %s' % len(subhub.models.DistributionTask.objects.all()))
            except Exception, e:
                log.warning(u'Unable to publish %s for feed %s : %s' % (instance, feed_url, e))
    elif isinstance(instance, subhub.models.DistributionTask) and maintenance:
        try:
            nb = len(subhub.models.DistributionTask.objects.all())
            log.debug("before call ENQUEUE, tasks %s" % nb)
            LastDTProcess.update()
            django_rq.enqueue(letsCallDistributionTaskProcess, threading.currentThread().name)
            log.debug('after call ENQUEUE')
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
            instance.unsubscribeToUpdades()


def listener(notification, **kwargs):
    ''' Process new content being provided by hub
    '''
    log.debug("enter listener args %s" % kwargs)
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
        # This is a temporairy work around. data.economie-solidaire.fr is not
        # yet responding. TODO we have to deal with contexts as tags come thesaurus
        try:
            # TEMP hard coded
            thessEndPoint = 'http://localhost:8080/openrdf-workbench/repositories/thessRepository/query'
            graph = ConjunctiveGraph('SPARQLStore')
            graph.open(thessEndPoint, False)
            ctx = 'http://%s' % settings.DEFAULT_URI_DOMAIN
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
            log.debug(u"Handle uri %s" % uri)
        except Exception, e:
            log.error(u"%s" % e)

    # update
    if obj:
        obj.updateFromRdf(g)


