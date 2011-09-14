# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import json
import tempfile

class Command(BaseCommand):
    help = u"Rename coop_page.page into coop_tree.article and url into link in a json dump"

    def handle(self, *args, **options):
        try:
            filename = args[0]
        except IndexError:
            print u'usage :', __name__.split('.')[-1], 'dumpfile.json'
            return
        
        try:
            dump_file = open(filename, 'r')
        except IOError:
            print filename, u"doesn't exist"
            return
        
        objects = json.loads(dump_file.read())
        dump_file.close()
        
        renaming = (
            ("coop_page.page", "coop_cms.article"),
            ("coop_tree.article", "coop_cms.article"),
            ("coop_tree.url", "coop_cms.link"),
            ("coop_tree.link", "coop_cms.link"),
            ("coop_tree.navnode", "coop_cms.navnode"),
            ("coop_tree.navigabletype", "coop_cms.navtype"),
            
        )
        renaming_ct = [(list(x.split('.')), list(y.split('.'))) for (x, y) in renaming]
        
        for obj in objects:
            for (old, new) in renaming:
                if obj["model"] == old:
                    obj["model"] = new
        
            for (old, new) in renaming_ct:
                if obj["fields"].has_key("content_type") and obj["fields"]["content_type"] == old:
                    obj["fields"]["content_type"] = new
            
        dump_file = open(filename, 'w')
        dump_file.write(json.dumps(objects, indent=4))
        dump_file.close()
        