# -*- coding: utf-8 -*-

from floppyforms.widgets import TextInput
from django.utils.encoding import force_unicode
from django.forms import Media
from django.core.urlresolvers import reverse

class AlohaInput(TextInput):
    template_name='djaloha/alohainput.html'
    
    #@property('media')
    def _media(self):
        css = {
            'all': ("aloha/plugins/at.tapo.aloha.plugins.Image/resources/imageplugin.css", )
        }
        js = (
            "aloha/aloha.js",
            "aloha/plugins/com.gentics.aloha.plugins.Format/plugin.js",
            "aloha/plugins/com.gentics.aloha.plugins.List/plugin.js",
            "aloha/plugins/com.gentics.aloha.plugins.HighlightEditables/plugin.js",
            "aloha/plugins/com.gentics.aloha.plugins.Table/plugin.js",
            "aloha/plugins/com.gentics.aloha.plugins.Link/plugin.js",
            "aloha/plugins/com.gentics.aloha.plugins.Link/LinkList.js",
            "aloha/plugins/com.gentics.aloha.plugins.Paste/plugin.js",
            "aloha/plugins/com.gentics.aloha.plugins.Paste/wordpastehandler.js",
            "aloha/plugins/at.tapo.aloha.plugins.Image/plugin.js",
            reverse('aloha_config')
        )
        return Media(css=css, js=js)
    media = property(_media)
