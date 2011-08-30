from django import forms
from models import NavigableType
from django.contrib.contenttypes.models import ContentType
from settings import get_navigable_content_types
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

class NavigableTypeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NavigableTypeForm, self).__init__(*args, **kwargs)
        self.fields['content_type'].widget = forms.Select(choices=get_navigable_content_types())
        
    def clean_label_rule(self):
        rule = self.cleaned_data['label_rule']
        if rule == NavigableType.LABEL_USE_GET_LABEL:
            ct = self.cleaned_data['content_type']
            if not 'get_label' in dir(ct.model_class()):
                raise ValidationError(_("Invalid rule for this content type: The object class doesn't have a get_label method"))
        return rule

    class Meta:
        model = NavigableType
