# -*- coding:utf-8 -*-
from coop.models import StaticURIModel
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.signals import  request_finished
# from coop_local.models import Organization
from django_push.publisher import ping_hub
from django.contrib.sites.models import Site


from rq import Queue, use_connection
use_connection()
q = Queue()


# Listener tool
@receiver(post_save)
def post_save_callback(sender, **kwargs):
    if StaticURIModel in sender.__mro__:
        print "before ping"
        try:
            # to be able to work offline
            q.enqueue(ping_hub, 'http://%s/%s/%s' % (Site.objects.get_current(), 'feed', sender.__name__.lower()))
        except:
            pass

request_finished.connect(post_save_callback)
# request_started.connect(post_save_callback)




# Asyncron version with the help of celeri
# see : http://dougalmatthews.com/2011/10/10/making-django%27s-signals-asynchronous-with-celery/
# from celery.task import task
# from django.db.models.signals import post_save

# @task(ignore_result=True)
# def async_post_save(sender, instance, **kwargs):
#     # do something with the instance.
#     if StaticURIModel in sender.__mro__:
#         print "before ping"
#         try:
#             # to be able to work offline
#             ping_hub('http://%s/%s/%s' % (Site.objects.get_current(), 'feed', sender.__name__.lower()))
#         except:
#             pass

# # post_save.connect(async_post_save.delay, sender=StaticURIModel)
