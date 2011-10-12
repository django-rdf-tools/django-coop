#-*- coding: utf-8 -*-

from django.contrib.admin.widgets import AdminTextInputWidget
from django.forms import HiddenInput
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

def get_button_code(label, url):
    """create a html button"""
    return u"""&nbsp;&nbsp;<input type="button" value="{0}" onclick="window.location={1}" />""".format(label, url)
    
class AdminCollectRssWidget(HiddenInput):
    """
    Widget for RssSource id
    The id is hidden and replaced by an action button calling the collect_rss_items view
    """
    def render(self, name, value, attrs=None):
        widget = super(AdminCollectRssWidget, self).render(name, value, attrs)
        html = unicode(widget)
        
        #a bit tricky but the only way I know to get the object id for the button url
        base_url = reverse('rss_sync_collect_rss_items', args=[99])[:-2]
        url = "\'{0}\'+document.getElementById(\'{1}\').value".format(base_url, attrs['id'])
        
        html += get_button_code(_('Collect'), url)
 
        return mark_safe(html)

class AdminCreateArticleWidget(HiddenInput):
    """
    Widget for RssItem id
    The id is hidden and replaced by an action button which is creating a CMS article
    """
    
    def render(self, name, value, attrs=None):
        widget = super(AdminCreateArticleWidget, self).render(name, value, attrs)
        html = unicode(widget)
        
        #a bit tricky but the only way I know to get the object id for the button url
        base_url = reverse('rss_sync_create_cms_article', args=[99])[:-2]
        url = "\'{0}\'+document.getElementById(\'{1}\').value".format(base_url, attrs['id'])
        
        html += get_button_code(_('Create CMS article'), url)
 
        return mark_safe(html)
