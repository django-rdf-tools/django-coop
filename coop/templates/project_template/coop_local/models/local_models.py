# -*- coding:utf-8 -*-
from django.db import models
from extended_choices import Choices


# Use Choices() !
# ETAT = ((0, 'Inconnu'),
#         (1, 'Active'),
#         (2, 'En sommeil'),
#         (3, 'En projet'),
# )

# Here you can either :
# - Customize coop models by deriving from the abstract class (BaseOrganization, Baseperson...)
# - Or add your own models, providing you add in their Meta class app_label="coop_local"