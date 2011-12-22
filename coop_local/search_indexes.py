import datetime
from haystack import indexes, site
from coop_local.models import Initiative

class InitiativeIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    acronym = indexes.CharField(model_attr='acronym')
    description = indexes.CharField(model_attr='description')
    tags = indexes.MultiValueField()
    
    def prepare_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]
    
site.register(Initiative,InitiativeIndex)