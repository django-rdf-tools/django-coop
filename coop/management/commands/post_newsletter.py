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
        # self.emails = 
        # if len(args)>0:
        #     dests = args[0].split(";")
        # else:
        #     print 'usage: python manage.py post_newsletter toto@toto.fr;titi@titi.fr'

        sendings = NewsletterSending.objects.filter(scheduling_dt__lte=datetime.now(), sending_dt=None)
        for sending in sendings:
            print sending
            # dests = map(lambda x: x.email, sending.newsletter.lists.all())
            
            dests = []
            tags = []

            for ml in sending.newsletter.lists.all():
                tags.append(ml.name)
                for dest in ml.dest_dicts():
                    dests.append(dest)

            if self.verbosity >= 1:
                print 'send_newsletter {1} to {0} addresses'.format(len(dests), sending.newsletter)
            if self.verbosity >= 2:
                for d in dests:
                    print 'email : %s' % d['email']

            nb_sent = send_newsletter(sending.newsletter, dests, tags)
            if self.verbosity >= 1:
                print nb_sent, "emails sent"

            sending.sending_dt = datetime.now()
            sending.save()
