# -*- coding:utf-8 -*-
from optparse import make_option
from django.core.management.base import BaseCommand
import coop


class Command(BaseCommand):
    help = "Dump in rdf format all data."
    base_options = (
        make_option('--format', dest='rdfformat', default="xml",
            help='The rdf format (default is xml), possible values are "n3", "json", and "ttl".'
        ),
        make_option("-o", "--output", dest="output_file", default="all",
            help='The output file.'
        ),
        make_option("-m", "--model", dest="model", default=None,
            help='A specif model, default value is None and in this case objects from all models are dump.'
        ),
    )
    option_list = BaseCommand.option_list + base_options

    def handle(self, **options):
        format = options.get('rdfformat')
        dest = options.get('output_file')
        model = options.get('model')
        if not model == None:
            model = model.lower()
        coop.models.rdfDumpAll(dest, format, model)

