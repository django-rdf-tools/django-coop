import types

from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, TemplateDoesNotExist
from django.utils.decorators import classonlymethod

from django_conneg.views import ContentNegotiatedView
from django_conneg.decorators import renderer as conneg_renderer


from django_webid.provider.models import WebIDUser

import n3proxy
from coop_local.models import Person


class PriorityContentNegotiatedView(ContentNegotiatedView):
    """
    dynamic addition
    of renderers
    """

    @classonlymethod
    def as_view(cls, **initkwargs):
        ranked_mimetypes = getattr(cls, '_mimetypes', None)
        if ranked_mimetypes:
            for mime, prio, name in ranked_mimetypes:
                renderer = cls.getRenderer(name, mime, name, prio)
                cls.addMethod(renderer)
        view = super(PriorityContentNegotiatedView, cls).as_view(**initkwargs)
        return view

    @classonlymethod
    def addMethod(cls, func):
        return setattr(cls, func.__name__, types.MethodType(func, cls))

    @classonlymethod
    def getRenderer(cls, format, mimetypes, name, priority):
        if not isinstance(mimetypes, tuple):
            mimetypes = (mimetypes,)
        mime = mimetypes[0]
        
        def renderer(cls, self, request, context, template_name):
            template_name = self.join_template_name(template_name, name.lower())
            if template_name is None:
                return NotImplemented
            try:
                return render_to_response(template_name,
                                          context,
                                          context_instance=RequestContext(request),
                                          mimetype=mime)
            except TemplateDoesNotExist:
                return NotImplemented

        renderer.__name__ = 'render_%s' % mime.replace('/', '_')
        renderer = conneg_renderer(format=format,
                                       mimetypes=mimetypes,
                                       priority=priority)(renderer)
        return renderer


class WebIDProfileView(PriorityContentNegotiatedView):
    """
    View that negotiates the output format
    Supports: html, rdfa, rdf+xml, xhtml, turtle
    ... why not vcard???
    """
    _default_format = 'html'
    #fallback format???
    #_force_fallback_format = 'html'
    _mimetypes = (('text/html', 10, 'html'),
                  ('application/xhtml+xml', 5, 'rdfa'),
                  ('application/rdf+xml', 1, 'rdfxml'),
                  ('text/turtle', 2, 'turtle'))

    def get(self, request, username=None):
        webiduser = get_object_or_404(WebIDUser,
            username=username)
        try:
            person = webiduser.get_profile()
        except Person.DoesNotExist:
            raise Http404
        D2RQ_ROOT = settings.D2RQ_ROOT
        #profileuri = "%spage/coop_local_person/%s/" % (D2RQ_ROOT, person.id)
        # TODO ; devrait disparaitre, uriredirect fait le  boulot
        n3uri = "%sdata/coop_local_person/%s/" % (D2RQ_ROOT, person.id)
        rdfgraph = n3proxy.augment_user_profile(webiduser, n3uri).serialize()

        context = {
                "webiduser": webiduser,
                "xmlpayload": rdfgraph,
                "MEDIA_URL": settings.MEDIA_URL,
                "STATIC_URL": settings.STATIC_URL,
        }
        # Call render, passing a template name (w/o file extension)
        return self.render(request, context,
                'webid/profiles/webid')

    # fix head method
    # (fixed in bennomadic fork of django_conneg, which is now
    # in requirements, let's see if it's merged upstream.)

    #def head(self, request, *args, **kwargs):
    #    return self.get(request, *args, **kwargs)
