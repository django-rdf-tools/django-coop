# -*- coding:utf-8 -*-
from coop.models import StaticURIModel
from django.db.models.signals import post_save
from django.dispatch import receiver
# from django.core.signals import  request_finished
# from coop_local.models import Organization
from django.contrib.sites.models import Site
import subhub
import logging

# import django_rq
# redis_conn = django_rq.get_connection('high')
# q = django_rq.get_queue('high')



# Workaround for rqworker limitation
def letsCallDistributionTaskProcess():
    subhub.models.DistributionTask.objects.process()


log = logging.getLogger('subhub.maintenance')


# Listener tool
@receiver(post_save)
def post_save_callback(sender, instance, **kwargs):
    print "Post save callback with sender %s and instance %s" % (sender, instance)
    if StaticURIModel in sender.__mro__:
        # to be able to work offline
        feed_url = 'http://%s/feed/%s/' % (Site.objects.get_current().domain, sender.__name__.lower())
        # print "publish for topic with feed %s  and instance %s" % (feed_url, instance)
        subhub.publish([feed_url], instance.get_absolute_url(), False)
        q.enqueue(letsCallDistributionTaskProcess)
    elif isinstance(instance, subhub.models.SubscriptionTask):
        # call the maintenance
            print "Call the maintenance"
            try:
                log.info('Processing verification queue...')
                subhub.models.SubscriptionTask.objects.process(log=log)
            except subhub.utils.LockError, e:
                log.warning(str(e))
    else:
        pass
