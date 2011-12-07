# -*- coding:utf-8 -*-
from django.db import models
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from coop_geo.models import Location

class BaseSite(models.Model):
    title = models.CharField(_('Titre'),null=True,blank=True,max_length=250)
    description = models.TextField(_(u'Description'),null=True,blank=True)
    site_principal = models.BooleanField(default=False)
    uri = models.CharField(_(u'URI principale'),null=True,blank=True, max_length=250, editable=False)
    
    location = models.ForeignKey(Location, related_name='sites')
    initiative = models.ForeignKey('coop_local.Initiative',null=True,blank=True,related_name='sites')

    


#tout ça peut gicler maintenant    
    adr1 = models.CharField(null=True,blank=True, max_length=100, editable=False)
    adr2 = models.CharField(null=True,blank=True, max_length=100, editable=False)
    zipcode = models.CharField(null=True,blank=True, max_length=5, editable=False)
    city = models.CharField(null=True,blank=True, max_length=100, editable=False)
    latlong = models.CharField(null=True,blank=True, max_length=100, editable=False)
    lat = models.CharField(null=True,blank=True, max_length=100, editable=False)
    long = models.CharField(null=True,blank=True, max_length=100, editable=False)
    
# par contre transférer ici : tel, fax, portable, email    
    
    
    created = exfields.CreationDateTimeField(_(u'Création'),null=True)
    modified = exfields.ModificationDateTimeField(_(u'Modification'),null=True)
    uuid = exfields.UUIDField(null=True) #nécessaire pour URI de l'engagement
    class Meta:
        abstract = True
    def __unicode__(self):
        if self.title != None:
            return unicode(self.title)+u', '+unicode(self.city)
        else:
            return unicode(self.adr1)+u', '+unicode(self.city)
    def get_absolute_url(self):
        return reverse('place_detail', args=[self.uuid])
    #TODO def save si le seul alors principal, si un autre est principal alors erreur
