from django import forms
from models import NavigableType
from django.contrib.contenttypes.models import ContentType
from settings import get_navigable_content_types

class NavigableTypeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NavigableTypeForm, self).__init__(*args, **kwargs)
        self.fields['content_type'].widget = forms.Select(choices=get_navigable_content_types())

    class Meta:
        model = NavigableType
