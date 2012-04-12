# -*- coding:utf-8 -*-
from django.db import models
from django.contrib.sites.models import Site


class URIModel(models.Model):
    """
    To use this model as a basis for your own abstract model, you need to have
    a 'uri_id' property set and a string for the model type URL representation :

    @property
    def uri_id(self):
        return self.username # example with username

    uri_fragment = 'org'    

    the uri_fragment can then be overriden in a real model derived from your abstract model

    """
    class Meta:
        abstract = True

    def init_uri(self):
        return 'http://' + str(Site.objects.get_current().domain) + \
                    '/id/'+ str(self.uri_fragment) + \
                    '/' + str(getattr(self, 'uri_id')) + '/'

    def save(self, *args, **kwargs):
        # create / update URI
        if self.uri != self.init_uri():
            self.uri = self.init_uri()
        super(URIModel, self).save(*args, **kwargs)
