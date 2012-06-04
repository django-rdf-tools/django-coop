# -*- coding:utf-8 -*-
from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from extended_choices import Choices
import shortuuid

URI_MODE = Choices(
    ('LOCAL',  1, _(u'Local')),
    ('COMMON',   2, _(u'Common')),
    ('IMPORTED', 3, _(u'Imported')),
)


class URIModel(models.Model):
    """
    To use this model as a basis for your own abstract model, you need to have
    a 'uri_id' property set and a string for the model type URL representation :

    @property
    def uri_id(self):
        return self.username # example with username

    uri_registry = 'org'    

    the uri_fragment can then be overriden in a real model derived from your abstract model

    """
    class Meta:
        abstract = True

    uri_mode = models.PositiveSmallIntegerField(_(u'Mode'), choices=URI_MODE.CHOICES, default=URI_MODE.LOCAL, editable=False)
    uri = models.CharField(_(u'main URI'), blank=True, null=True,
                            max_length=250, editable=False)  # FIXME : null=True incompatible with unique=True
    # Le code suivante ne marche pas avec south et pourtant il correxpond exactement à ce que je voudrais
    # faire. Si on supprime unique=True, alors la migration se passe bien, mais toutes les
    # du model ont la meme valeur.... Et bien sur, si on met uniaue=True, south rale car 
    # le champs n'est pas unique.
    # South n'a pas l'air capable de traiter ce cas.
    # D'apres la doc, il est possible de le faire en 3 fois, sans utiliser le default, avec
    # un datamigration (voir la doc Part 3: Advanced Commands and Data Migrations)
    
    #uuid = models.CharField(_(u'uuid'), max_length=50, default=shortuuid.uuid, unique=True) 

    # La version simple c'est de passer par le save() et de supprimer le default.... c'est pas 
    # tres beau, car un plus couteux en runtime... mais bon
    uuid = models.CharField(_(u'uuid'), max_length=50, null=True, default=shortuuid.uuid, editable=False) 

    # the default value, this attribut should be overloaded
    domain_name = settings.DEFAULT_URI_DOMAIN
    #str(Site.objects.get_current().domain)

    # This metho could be overwritten by subClasses
    @property
    def uri_id(self):
        return self.uuid

    def uri_registry(self):
        return self.__class__.__name__.lower()

    def init_uri(self):
        #self.uuid = shortuuid.uuid() 
        return 'http://' + self.domain_name + \
                    '/id/' + self.uri_registry() + \
                    '/' + str(getattr(self, 'uri_id')) + '/'

    # self.uri est null ou vide le creer (cad appel init_uri)
    # si le domain a changé alors changer l'uri (cad dire appel init_uri)
    # si le uri_registery a changer alors changer l'uri
    # attention dans les 2 cas le uuid ne bouge pas.... il faut alors aller le chercher
    #
    # repenser aux commons et aux importés pour voir si tout marche

    def save(self, *args, **kwargs):
        super(URIModel, self).save(*args, **kwargs)
         # create / update URI
        if self.uri_mode != URI_MODE.IMPORTED:
            if not self.uri or self.uri == '':
                #self.uuid = shortuuid.uuid() 
                self.uri = self.init_uri()
            else:
                # l'uri est déjà en db, mais il n'est peut etre pas à jour...
                # si le domaine_name a changé.... on va alors transporter les uri
                # ou si le uri_registery a changé, on veut un nom plus approprié
                # il faudrait aussi vérifier que le uri_id n'a pas changé...
                without_scheme = str(self.uri[7:])  # forget 'http://'
                sp = without_scheme.split('/')
                assert(sp[1] == 'id')  # to assert a minimal coherence...
                # on va recuper la valeur de uri_id qui est stockée en bd
                # c'est uri_id qui sera perdu, c'est normal ca cela veut dire que 
                # l'uri stock en db n'est pas a jour (cas du role dont le nom a changé
                # et donc son slug et donc l'uri aussi doit suivre)

#TODO il faudrait essayer d'imaginer ce qui a le plus de probabilité de changer...
# le domaine c'est rare 'en tout cas en phase d'exploitation), il doit donc arriver en dernier
# uri_id ne changera pas pour plein de models (ceux dénotés par STATES.LOCAL)
# par contre pour les models dénoté par STATES.COMMON c'est peut etre moin rare
# pour le registry_uri ca ne devrait pas trop bouger en phase de production donc a la fin aussi
                if sp[3] != self.uri_id:
                    self.uri = self.init_uri()
                else:
                    if sp[0] != self.domain_name:
                        self.uri = self.init_uri()
                    else:
                        if  sp[2] != self.uri_registry():
                            self.uri = self.init_uri()

        super(URIModel, self).save(*args, **kwargs)
