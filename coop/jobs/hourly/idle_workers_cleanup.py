# -*- coding:utf-8 -*-
"""
Hourly cleanup job.

Can be run as a cronjob to clean out old idle RQ workers. The point with RQ workers
is that they need two SIGINT signals to die this is not possible with supervisor
or other circus.... some workers may stay idle It is a good idea to clean them;
"""

import logging
from django.conf import settings
from redis import Redis
from django_extensions.management.jobs import HourlyJob
from rq import Queue, use_connection, get_current_connection, Worker

# As subhub is the only app the use redis. All Redis stuff are logger 
# subhub.mainteance  log
log = logging.getLogger('subhub.maintenance')


class Job(HourlyJob):
    help = "RQ idle workers cleanup Job"

    def execute(self):
        # It is always possible that the Redis connection is not yet set 
        print "ENTER"
        if not get_current_connection():
            conn = Redis('localhost', settings.REDIS_PORT)
            use_connection(conn)
        if not get_current_connection():
            log.error(u'Unable to create redis connection')
        # use the 'default' queue. We only used this one;
        q = Queue()
        # if the queue is not empty then some old idle workers may have to be cleaned
        if not q.is_empty():
            for w in Worker.all():
                if w.state == 'idle' and q in w.queues:
                    log.info(u'Work %s will die gently' % w.name)
                    w.register_death()
