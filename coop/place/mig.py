
# custom data migrations, utiles juste une fois...

from coop_local.models import Initiative,Site
from django.contrib.gis.geos import Point



def create_locations():
    sites = Site.objects.all()
    for s in sites :
        if s.title != '' :
            label = s.title
        else:
            label = s.adr1
        p = Point(float(s.long),float(s.lat))    
        loc = Location(label=label,point=p)
        loc.save()
        s.location = loc
        s.save()

def missing_sites():    
    sites = Site.objects.all()
    for site in sites :
        init_linked = site.initiative_set.all()
        if len(init_linked) > 1 : 
            print init_linked
            for init in init_linked[1:]:
                print init
                ancien_site = init.sites.all()[0]
                print 'old',ancien_site.id
                init.sites.remove(ancien_site)
                if len(init.sites.all()) == 0:
                    new_site = site
                    new_site.pk = None
                    new_site.save()
                    print 'new',new_site.id
                    init.sites.add(new_site)
                    print 'sites',init.sites.all()
                    init.save()

def relink_sites():
    sites = Site.objects.all()
    for site in sites :
        init = site.old_rel.all()[0]
        site.initiative = init
        site.save()
        
                     