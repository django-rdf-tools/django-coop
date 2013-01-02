# -*- coding:utf-8 -*-
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, pre_delete
from django.conf import settings


newletters_item__class = models.get_model('coop_local', 'newsletteritem')


#delete item when content object is deleted
def on_delete_newsletterable_item(sender, instance, **kwargs):
    if sender in settings.COOP_NEWLETTER_ITEM_CLASSES:
        if hasattr(instance, 'id'):
            try:
                ct = ContentType.objects.get_for_model(instance)
                item = newletters_item__class.objects.get(content_type=ct, object_id=instance.id)
                item.delete()
            except (newletters_item__class.DoesNotExist, ContentType.DoesNotExist):
                pass
pre_delete.connect(on_delete_newsletterable_item)


def create_newsletter_item(instance):
    ct = ContentType.objects.get_for_model(instance)
    if getattr(instance, 'in_newsletter', True):
        #Create a newsletter item automatically
        #An optional 'in_newsletter' field can skip the automatic creation if set to False
        return newletters_item__class.objects.get_or_create(content_type=ct, object_id=instance.id)
    elif hasattr(instance, 'in_newsletter'):
        #If 'in_newsletter' field existe and is False
        #We delete the Item if exists
        try:
            item = newletters_item__class.objects.get(content_type=ct, object_id=instance.id)
            item.delete()
            return None, True
        except newletters_item__class.DoesNotExist:
            return None, False


#create automatically a newsletter item for every objects configured as newsletter_item
def on_create_newsletterable_instance(sender, instance, created, raw, **kwargs):
    if sender in settings.COOP_NEWLETTER_ITEM_CLASSES:
        create_newsletter_item(instance)
post_save.connect(on_create_newsletterable_instance)

