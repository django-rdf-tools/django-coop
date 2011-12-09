# -*- coding:utf-8 -*-
from django.db import models
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from coop_geo.models import Location

class BaseSite(models.Model):
    title = models.CharField(_('title'),null=True,blank=True,max_length=250)
    description = models.TextField(_(u'description'),null=True,blank=True)
    site_principal = models.BooleanField(default=False)
    
    uri = models.CharField(_(u'main URI'),null=True,blank=True, max_length=250, editable=False)
    
    location = models.ForeignKey(Location, related_name='sites')
    initiative = models.ForeignKey('coop_local.Initiative',null=True,blank=True,related_name='sites')

    telephone_fixe = models.CharField(_(u'Téléphone fixe'),blank=True,null=True, max_length=14)

#tout ça peut gicler maintenant    
    adr1 = models.CharField(null=True,blank=True, max_length=100, editable=False)
    adr2 = models.CharField(null=True,blank=True, max_length=100, editable=False)
    zipcode = models.CharField(null=True,blank=True, max_length=5, editable=False)
    city = models.CharField(null=True,blank=True, max_length=100, editable=False)
    latlong = models.CharField(null=True,blank=True, max_length=100, editable=False)
    lat = models.CharField(null=True,blank=True, max_length=100, editable=False)
    long = models.CharField(null=True,blank=True, max_length=100, editable=False)
    
# par contre transférer ici : tel, fax, portable, email    
    
    created = exfields.CreationDateTimeField(_(u'created'),null=True)
    modified = exfields.ModificationDateTimeField(_(u'modified'),null=True)
    uuid = exfields.UUIDField(null=True) #nécessaire pour URI
    
    class Meta:
        abstract = True
        verbose_name = _(u'Point de présence')
        verbose_name_plural = _(u'Points de présence')
        
    def __unicode__(self):
        if self.title != None:
            return unicode(self.title)+u', '+unicode(self.city)
        else:
            return unicode(self.adr1)+u', '+unicode(self.city)
    def get_absolute_url(self):
        return reverse('place_detail', args=[self.uuid])
        
    #TODO def save si le seul alors principal, si un autre est principal alors erreur
