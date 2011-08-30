from django import forms
from models import NavigableType
from django.contrib.contenttypes.models import ContentType
import config # not unused, needed by livesettings !
from livesettings import config_value

class NavigableTypeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NavigableTypeForm, self).__init__(*args, **kwargs)
        self.fields['content_type'] = forms.ChoiceField(choices = self.get_navigable_content_types())
        print self.fields['content_type'].choices

    def get_navigable_content_types(self):
        ct_choices = []
        content_apps = config_value('coop_tree', 'CONTENT_APPS')
        navigable_content_types = ContentType.objects.filter(app_label__in=content_apps).order_by('app_label')
        for ct in navigable_content_types:
            is_navnode = ((ct.model == 'navnode') and (ct.app_label == 'coop_tree'))
            if (not is_navnode) and 'get_absolute_url' in dir(ct.model_class()):
                ct_name = ct.app_label+u'.'+ct.model
                ct_choices.append((ct_name, ct_name))
        return ct_choices
        
    def clean_content_type(self):
        app_label, model_name = self.cleaned_data['content_type'].split('.')
        ct = ContentType.objects.get(app_label=app_label, model=model_name)
        return ct

    class Meta:
        model = NavigableType