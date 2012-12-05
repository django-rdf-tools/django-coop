from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.sites.models import get_current_site

def current_site(request):
    '''
    A context processor to add the "current site" to the current Context
    '''
    try:
        current_site = get_current_site(request)
        return {
            'current_site': current_site,
            'site_author': settings.SITE_AUTHOR,
            'site_title': current_site.name,
        }
    except Site.DoesNotExist:
        # always return a dict, no matter what!
        return {'current_site':''} # an empty string

