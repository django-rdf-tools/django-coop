from django.conf import settings
from django.db.models.loading import get_model

# define the minimal weight of a tag in the tagcloud
TAGCLOUD_MIN = getattr(settings, 'TAGGIT_TAGCLOUD_MIN', 1.0)

# define the maximum weight of a tag in the tagcloud 
TAGCLOUD_MAX = getattr(settings, 'TAGGIT_TAGCLOUD_MAX', 6.0) 

# define the default models for tags and tagged items
TAG_MODEL = getattr(settings, 'TAGGIT_TAG_MODEL', ('taggit', 'Tag'))
TAG_MODEL = get_model(*TAG_MODEL)
TAGGED_ITEM_MODEL = getattr(settings, 'TAGGIT_TAGGED_ITEM_MODEL', \
                            ('taggit','TaggedItem'))
TAGGED_ITEM_MODEL = get_model(*TAGGED_ITEM_MODEL)
