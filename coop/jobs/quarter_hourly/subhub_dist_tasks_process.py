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
import subhub

# As subhub is the only app the use redis. All Redis stuff are logger 
# subhub.mainteance  log
log = logging.getLogger('subhub.maintenance')


class Job(QuarterHourlyJob):
    help = "subhub DistributionTasks process"

    def execute(self):
        dt = subhub.models.DistributionTask.objects.all()
        if len(dt) > 0 and settings.SUBHUB_MAINTENANCE_AUTO:
            subhub.models.DistributionTask.objects.process(log=log)



