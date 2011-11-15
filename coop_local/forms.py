#!/usr/bin/env python
# -*- coding:utf-8 -*-

from coop.place.forms import BaseSiteForm
import models

class SiteForm(BaseSiteForm):
    class Meta:
        model = models.Site
