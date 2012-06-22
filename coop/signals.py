# -*- coding:utf-8 -*-
from coop.models import StaticURIModel
from django.db.models.signals import post_save
from django.dispatch import receiver
# from django.core.signals import  request_finished
# from coop_local.models import Organization
from django_push.publisher import ping_hub
from django.contrib.sites.models import Site


from rq import Queue, use_connection
use_connection()
q = Queue()


# Listener tool
@receiver(post_save)
def post_save_callback(sender, instance, **kwargs):
    if StaticURIModel in sender.__mro__:
        # to be able to work offline
        try:
            feed_url = 'http://%s/%s/%s/' % (Site.objects.get_current(), 'feed', sender.__name__.lower())
            print "ping hub for %s " % feed_url
            # ping_hub(feed_url)
            q.enqueue(ping_hub, feed_url)
        except:
            pass

# request_finished.connect(post_save_callback)
# request_started.connect(post_save_callback)




#