# -*- coding:utf-8 -*-
"""
As DistributionTasks.objects.process is call on post_save signal (when a DistributionTasks) is created.
It is always possible that a Tasks could be distributed ... timeout, exception, ....error 500
This job is in charge to try again.
Redis Failed queue should also be handled.

At least, dequeud

"""

import logging
from django.conf import settings
from django_extensions.management.jobs import QuarterHourlyJob
from rq import Queue, get_current_connection
import subhub
from coop.signals import letsCallDistributionTaskProcess

# As subhub is the only app the use redis. All Redis stuff are logger 
# subhub.mainteance  log
log = logging.getLogger('subhub.maintenance')


class Job(QuarterHourlyJob):
    help = "subhub DistributionTasks process"

    def execute(self):
        if get_current_connection():
            q = Queue('failed')
            try:
                # TODO:  well jobs could be retried.... 
                while not q.is_empty():
                    q.dequeue()
            except Exception, e:
                log.error(u'Coud not dequeue redis failed queue: %s' % e)

            dt = subhub.models.DistributionTask.objects.all()
            if len(dt) > 0 and settings.SUBHUB_MAINTENANCE_AUTO:
                q = Queue()
                try:
                    q.enqueue(letsCallDistributionTaskProcess)
                except Exception, e:
                    log.error(u"Exception caught %s" % e)

        else:
            log.info(u"Redis connection not ready, wait and see")



