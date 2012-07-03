# -*- coding:utf-8 -*-
from coop.models import StaticURIModel
from django.db.models.signals import post_save
from django.dispatch import receiver
# from django.core.signals import  request_finished
# from coop_local.models import Organization
from django.contrib.sites.models import Site
from django.conf import  settings
import subhub
import logging
from redis.exceptions import ConnectionError


log = logging.getLogger('subhub.maintenance')

try:
    import django_rq
    redis_conn = django_rq.get_connection('high')
    q = django_rq.get_queue('high')
except:
    log.warning('Redis is not enabled')
    pass


# Workaround for rqworker limitation
def letsCallDistributionTaskProcess():
    subhub.models.DistributionTask.objects.process()


# Listener tool
@receiver(post_save)
def post_save_callback(sender, instance, **kwargs):
    log.debug(u"Post save callback with sender %s and instance %s" % (sender, instance))
    if StaticURIModel in sender.__mro__:
        feed_url = 'http://%s/feed/%s/' % (Site.objects.get_current().domain, sender.__name__.lower())
        try:
            subhub.publish([feed_url], instance.uri, False)
        except Exception, e:
            log.warning(u'Unable to publish %s for feed %s : %s' % (instance, feed_url, e))
        if settings.SUBHUB_MAINTENANCE_AUTO:
            try:
                q.enqueue(letsCallDistributionTaskProcess)
            except ConnectionError, e:
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
