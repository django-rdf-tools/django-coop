#-*- coding: utf-8 -*-

from django.contrib.admin.widgets import AdminTextInputWidget
from django.forms import HiddenInput
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from rss_sync.models import RssSource

def get_button_code(label, url, is_default=False):
    """create a html button"""
    css_class = u' default' if is_default else ''
    html = u"""&nbsp;&nbsp;<input class="cust-btn{2}" type="button" value="{0}" onclick="window.location=\'{1}\'" />""".format(
        label, url, css_class)
    #javascript code for moving the button to the submit-row at the bottom of the page
    html += u"<script>django.jQuery(function() {django.jQuery('.cust-btn').appendTo('.submit-row')});</script>"
    return html
    
class AdminCollectRssWidget(HiddenInput):
    """
    Widget for RssSource id
    The id is hidden and replaced by an action button calling the collect_rss_items view
    """
    def render(self, name, value, attrs=None):
        widget = super(AdminCollectRssWidget, self).render(name, value, attrs)
        html = unicode(widget)
        
        html += value
        
        id = RssSource.objects.get(url=value).id
        
        url = reverse('rss_sync_collect_rss_items', args=[id])
    
        html += get_button_code(_('Collect'), url, True)
 
        return mark_safe(html)

class AdminCreateArticleWidget(HiddenInput):
    """
    Widget for RssItem id
    The id is hidden and replaced by an action button which is creating a CMS article
    """
    
    def render(self, name, value, attrs=None):
        widget = super(AdminCreateArticleWidget, self).render(name, value, attrs)
        html = unicode(widget)
        
        html += unicode(value)
        
        url = reverse('rss_sync_create_cms_article', args=[int(value)])
        
        html += get_button_code(_('Create CMS article'), url)
 
        return mark_safe(html)
