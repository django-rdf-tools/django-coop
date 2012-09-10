from django.shortcuts import render, render_to_response , get_object_or_404
from django_webid.provider.models import WebIDUser
from django.contrib.auth.models import User
from django.http import Http404
from django.conf import settings

from coop_local.models import Person
from .n3proxy import augment_user_profile

#from django.contrib.auth.decorators import login_required


def people(request, username):
    webiduser = get_object_or_404(WebIDUser, username=username)
    try:
        person = webiduser.get_profile()
    except Person.DoesNotExist:
        raise Http404

    D2RQ_ROOT = settings.D2RQ_ROOT
    profileuri = "%spage/coop_local_person/%s/" % (D2RQ_ROOT, person.id)
    n3uri = "%sdata/coop_local_person/%s/" % (D2RQ_ROOT, person.id)
    rdfgraph = augment_user_profile(webiduser, n3uri).serialize()

    #XXX DEBUG
    return render_to_response('webid/people.html', {
        'request': request,
        'user': request.user,
        'username': username,
        'webiduser': webiduser,
        'person_id': person.id,
        'n3uri': n3uri,
        'profileuri': profileuri,
        'rdfgraph': rdfgraph,
        'STATIC_URL': settings.STATIC_URL,
        'MEDIA_URL': settings.MEDIA_URL})


#@login_required
#XXX is this decodator working as expected?
#I think we need a webidlogin_required...
def test_login(request):
    return render_to_response('webid/auth/testlogin.html', {
        'request': request,
        'user': request.user,
        'webidinfo': getattr(request, 'webidinfo', None),
        'STATIC_URL': settings.STATIC_URL,
        'MEDIA_URL': settings.MEDIA_URL,
        })


def webidlogin_report(request):
    if settings.DEBUG:
        content_type = "text/xml"
    else:
        content_type = "application/rdf+xml"
    return render(request,
        'webid/auth/webidloginReport.html',
        {'user': request.user,
         'request': request,
         'webidinfo': request.webidinfo},
         content_type=content_type,
        )
