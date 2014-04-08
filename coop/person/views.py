# -*- coding:utf-8 -*-
from django.conf import settings
from django.shortcuts import render_to_response, redirect, get_object_or_404
from coop_local.models import Organization, Person, Article
from django.template import RequestContext
from django.core.urlresolvers import reverse
from coop.forms import PersonContact


def public_profile(request, uuid):
    context = {'form': PersonContact}
    person = get_object_or_404(Person, uuid=uuid, sites__id=settings.SITE_ID)
    if request.method == "POST":
        form = PersonContact(request.POST)
        if form.is_valid():
            from django.core.mail import send_mail
            send_mail(subject=u"Message posté via le site %s" % settings.SITE_TITLE,
                recipient_list=[person.pref_email.content],
                from_email=request.POST['sender'],
                message=request.POST['message'])
            context['msg_perso'] = u"Votre message a été envoyé à %s" % person.label()
        else:
            context['form'] = PersonContact(request.POST)
            context['error'] = u'Merci de corriger le formulaire'
    context['person'] = person
    context['articles'] = Article.objects.filter(person=person).order_by('-created')
    return render_to_response('person/public_profile.html', context, RequestContext(request))
