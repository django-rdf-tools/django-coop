# -*- coding:utf-8 -*-
from django.contrib.auth.models import User
from django import forms
from django.utils.translation import ugettext_lazy as _
from coop_local.models import Person

# Repiquage carrément du modèle
attrs_dict = { 'class': 'required' }

# from http://birdhouse.org/blog/2009/06/27/django-profiles/
class ProfileForm(forms.ModelForm):
  
    last_name = forms.CharField(max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_(u'name'),
                                )
    username = forms.RegexField(regex=r'^\w+$',
                                max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_("username"),
                                error_messages={ 'invalid': _("This value must contain only letters, numbers and underscores.") },
                                help_text=u"Ce nom d'utilisateur sera public, affiché à la place du nom pour les visiteurs anonymes du site (Google par exemple)"
                                )
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_("email address"),
                             help_text= _(u"your personal email")
                             )
                             
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        try:
            self.fields['email'].initial = self.instance.user.email
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['username'].initial = self.instance.user.username
        except User.DoesNotExist:
            pass
    
        self.fields.keyOrder = ['last_name','username','email', 'adresse','code_postal','ville','telephone_fixe','telephone_portable']
            
    class Meta:
        model = Person
        exclude = ('user',)
    def save(self, *args, **kwargs):
        """
        Update the primary email address on the related User object as well.
        """
        u = self.instance.user
        u.email = self.cleaned_data['email']
        u.last_name = self.cleaned_data['last_name']
        u.username = self.cleaned_data['username']
        u.save()
        profile = super(ProfileForm, self).save(*args,**kwargs)
        return profile

    