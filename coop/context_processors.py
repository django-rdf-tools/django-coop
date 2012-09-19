from django.conf import settings
from django.contrib.sites.models import Site

def current_site(request):
    '''
    A context processor to add the "current site" to the current Context
    '''
    try:
        current_site = Site.objects.get_current()
        return {
            'current_site': current_site,
            'site_author': settings.SITE_AUTHOR,
            'site_title': settings.SITE_TITLE,
        }
    except Site.DoesNotExist:
        # always return a dict, no matter what!
        return {'current_site':''} # an empty string

