# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from datetime import datetime
from coop.mailing.utils import send_newsletter
from coop_local.models import NewsletterSending


class Command(BaseCommand):
    help = u"send newsletter"

    def handle(self, *args, **options):
        #look for emailing to be sent
        self.verbosity = int(options.get('verbosity', 1))
        # if len(args)>0:
        #     dests = args[0].split(";")
        # else:
        #     print 'usage: python manage.py send_newsletter toto@toto.fr;titi@titi.fr'

        sendings = NewsletterSending.objects.filter(scheduling_dt__lte=datetime.now(), sending_dt=None)
        for sending in sendings:
            dests = map(lambda x: x.email, sending.newsletter.lists.all())
            if self.verbosity >= 2:
                print 'send_newsletter {1} to {0} addresses'.format(len(dests), sending.newsletter)
            if self.verbosity >= 3:
                for d in dests:
                    print 'address %s' % d

            nb_sent = send_newsletter(sending.newsletter, dests)
            if self.verbosity >= 2:
                print nb_sent, "emails sent"

            sending.sending_dt = datetime.now()
            sending.save()
