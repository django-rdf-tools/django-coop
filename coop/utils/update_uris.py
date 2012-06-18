from django.db import models
import coop
import shortuuid

ll = models.get_models()

for l in ll:
    if l.__mro__.__contains__(coop.models.URIModel):
        print 'Je fait un save sur les instances du models %s' % l
        for o in l.objects.all():
            if o.uuid == None or "-" in o.uuid:
                o.uuid = shortuuid.uuid()
            o.save()
