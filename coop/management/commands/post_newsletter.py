# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.core.management import CommandError
from datetime import datetime
from coop.mailing.utils import send_newsletter
from coop_local.models import NewsletterSending, Newsletter
import sys
import os
from optparse import make_option
from django.utils import translation
from django.conf import settings

class Command(BaseCommand):
    help = u"send newsletter"

    option_list = BaseCommand.option_list + (
        make_option(
            "-f", 
            "--file", 
            dest = "filename",
            help = "specify import file", 
            metavar = "FILE"
        ),
        make_option(
            "-n", 
            "--news", 
            dest = "newsletter",
            help = "specify newsletter id", 
            metavar = "NEWS"
        ),
    )

    def handle(self, *args, **options):
        #look for emailing to be sent
        self.verbosity = int(options.get('verbosity', 1))

        # if len(args)>0:
        #     dests = args[0].split(";")
        # else:
        #     print 'usage: python manage.py post_newsletter toto@toto.fr;titi@titi.fr'

        dests = []
        tags = []

        translation.activate(settings.LANGUAGE_CODE)

        # METHODE LIGNE DE COMMANDE AVEC FICHIER TEXTE

        if options['filename'] and options['newsletter'] :
            if not os.path.isfile(options['filename']) :
                raise CommandError("File does not exist at the specified path.")

            news = Newsletter.objects.get(id=options['newsletter'])    

            try:

                in_file = open(options['filename'], 'r')
                tags.append(options['filename'])
                for mail in in_file.readlines():
                    dests.append({'email': mail.rstrip('\n'),
                                'name': None,
                                'uuid': None
                                })

                nb_sent = send_newsletter(news, dests, tags)
                if self.verbosity >= 1:
                    print nb_sent, "emails sent"

            finally:
                in_file.close()

        # METHODE NORMALE (DEPUIS ADMIN MAILING)

        elif options['newsletter']:

            news = Newsletter.objects.get(id=options['newsletter'])

            for ml in news.lists.all():
                tags.append(ml.name)
                for dest in ml.dest_dicts():
                    dests.append(dest)

            if self.verbosity >= 1:
                print u'send_newsletter %d to %d addresses'% (news.id, len(dests))
                if self.verbosity >= 3:
                    for d in dests:
                        print 'email : %s' % d['email']
                nb_sent = send_newsletter(news, dests, tags, self.verbosity)
                if self.verbosity >= 1:
                    print nb_sent, "emails sent"

        else:

            print 'usage: python manage.py post_newsletter --news=15 --file=adresses.txt'

            # sendings = NewsletterSending.objects.filter(scheduling_dt__lte=datetime.now(), sending_dt=None)
            
            # for sending in sendings:
            #     print sending                

            #     for ml in sending.newsletter.lists.all():
            #         tags.append(ml.name)
            #         for dest in ml.dest_dicts():
            #             dests.append(dest)

            #     if self.verbosity >= 1:
            #         print u'send_newsletter %d to %d addresses'% (news.id, len(dests))
            #     if self.verbosity >= 2:
            #         for d in dests:
            #             print 'email : %s' % d['email']
            #     nb_sent = send_newsletter(sending.newsletter, dests, tags)
            #     if self.verbosity >= 1:
            #         print nb_sent, "emails sent"
            #     sending.sending_dt = datetime.now()
            #     sending.save()



