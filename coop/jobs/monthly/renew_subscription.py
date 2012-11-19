# -*- coding:utf-8 -*-
"""
As DistributionTasks.objects.process is call on post_save signal (when a DistributionTasks) is created.
It is always possible that a Tasks could be distributed ... timeout, exception, ....error 500
This job is in charge to try again.
Redis Failed queue should also be handled.

At least, dequeud

"""

from django_extensions.management.jobs import QuarterHourlyJob
from django_push.subscriber.models import Subscription



class Job(MonthlyJob):
    help = "renew all subscription"

    def execute(self):
        for s in Subscription.objects.all():
            Subscription.objects.subscribe(s.topic, hub=s.hub)

