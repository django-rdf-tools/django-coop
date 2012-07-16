# -*- coding:utf-8 -*-
from coop.models import StaticURIModel, URI_MODE
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.sites.models import Site
from django.conf import  settings
from rdflib import Graph
import subhub
import logging
from urlparse import urlsplit
from django.db.models.loading import get_model
from django.contrib.contenttypes.models import ContentType


log = logging.getLogger('subhub.maintenance')


# Each coop is connected to a single instance of Redis.
# So the 'use_connection' method seems to be the bet way to deal with connection
from redis import Redis
from rq import Queue, use_connection, get_current_connection
if not get_current_connection():
    conn = Redis('localhost', settings.REDIS_PORT)
    use_connection(conn)
if not get_current_connection():
    log.error(u'Unable to create redis connection')
# use the 'default' queue
q = Queue()



# Workaround for rqworker limitation
def letsCallDistributionTaskProcess():
    log.debug(u'IN QUEUE try to  know the numbers of tasks %s' %
        len(subhub.models.DistributionTask.objects.all()))
    subhub.models.DistributionTask.objects.process(log=log)


# Listener tool
# The point here is to be careful with synchronization.
# subhub.publish will create a new DistributionTask object (if no DistributioTask
# exists for this instance); So the signals will be call again, that why 
# the q.enqueue is done only when post_sae_callback is called with a DistributionTask
# as instance.
@receiver(post_save)
def post_save_callback(sender, instance, **kwargs):
    log.debug(u"Post save callback with sender %s and instance %s and AUTO %s" % (sender, instance, settings.SUBHUB_MAINTENANCE_AUTO))
    if isinstance(instance, StaticURIModel):
        if instance.uri_mode == URI_MODE.IMPORTED:
            log.debug(u"%s is imported. Nothing to publish, but subscription renew" % instance)
            instance.subscribeToUpdades()
            # TODO check if a subscription is done, either lets do it
        else:
            feed_url = 'http://%s/feed/%s/' % (Site.objects.get_current().domain, sender.__name__.lower())
            try:
                subhub.publish([feed_url], instance.uri, False)
                log.debug('publish done; Number of Dist task %s' % len(subhub.models.DistributionTask.objects.all()))
            except Exception, e:
                log.debug(u'Unable to publish %s for feed %s : %s' % (instance, feed_url, e))
    elif isinstance(instance, subhub.models.DistributionTask) and settings.SUBHUB_MAINTENANCE_AUTO:
        try:
            log.debug("before call ENQUEUE, tasks %s" % len(subhub.models.DistributionTask.objects.all()))
            q.enqueue(letsCallDistributionTaskProcess)

            log.debug('after call ENQUEUE')
        except Exception, e:
            log.warning(u"%s" % e)
    elif isinstance(instance, subhub.models.SubscriptionTask) and settings.SUBHUB_MAINTENANCE_AUTO:
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
            instance.unubscribeToUpdades()


def listener(notification, **kwargs):
    ''' Process new content being provided by hub
    '''
    log.debug("enter listener args %s" % kwargs)
    try:
        entry = notification.entries[0]
        uri = str(entry.summary)
        g = Graph()
        g.parse(uri)
        log.debug(u"Handle uri %s" % uri)
    except Exception, e:
        log.error(u"%s" % e)
    # We have to retreive the instance
    scheme, host, path, query, fragment = urlsplit(uri)
    sp = path.split('/')
    try:
        model = sp[len(sp) - 3]
        mType = ContentType.objects.get(model=model)
        obj = get_model(mType.app_label, model).objects.get(uri=uri)
        obj.updateFromRdf(g)
    except Exception, e:
        log.error(u'%s' % e)

