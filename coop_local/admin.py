# -*- coding:utf-8 -*-
from django.contrib import admin
from django.conf import settings

from coop_local.models import Person,PersonCategory, Role, Engagement, \
    OrganizationCategory, Organization, SeeAlsoLink, SameAsLink, Relation,\
    Exchange, PaymentModality, Contact
from coop.admin import BaseEngagementInline, \
    BaseOrganizationAdmin, BasePersonAdmin, \
    BaseRelationInline, BaseOrgInline, BaseExchangeInline, \
    BaseExchangeAdmin, BasePaymentInline

if "coop_geo" in settings.INSTALLED_APPS :
    from coop.admin import LocatedInline, AreaInline


from coop.utils.autocomplete_admin import FkAutocompleteAdmin,InlineAutocompleteAdmin

admin.site.register(Role)
admin.site.register(PersonCategory)
admin.site.register(OrganizationCategory)

#from genericadmin.admin import GenericAdminModelAdmin,GenericTabularInline
from django.contrib.contenttypes.generic import GenericTabularInline

class ContactInline(GenericTabularInline):
    model = Contact
    extra=1

class SeeAlsoInline(GenericTabularInline):
    model = SeeAlsoLink
    extra=1
    
class SameAsInline(GenericTabularInline):
    model = SameAsLink
    extra=1    

class PaymentInline(BasePaymentInline):
    model = PaymentModality

class ExchangeInline(BaseExchangeInline):
    model = Exchange
    fieldsets = ((None, {'fields' : ('title',
                                    ('etype','permanent','expiration'),
                                    'description','tags')}),)

class EngagementInline(BaseEngagementInline,InlineAutocompleteAdmin):
    model = Engagement

class OrgInline(BaseOrgInline,InlineAutocompleteAdmin):
    model = Engagement

class RelationInline(BaseRelationInline,InlineAutocompleteAdmin):
    model = Relation


class OrganizationAdmin(BaseOrganizationAdmin,FkAutocompleteAdmin):
    inlines = [
        ContactInline,
        EngagementInline,
        LocatedInline,  # CREDIS utilise coop-geo
        AreaInline,     # CREDIS utilise coop-geo
        RelationInline,
        SeeAlsoInline,
        ExchangeInline,
        ]
    list_display = ('logo_thumb','title','active','has_description','has_location') # has_location : CREDIS utilise coop-geo
    fieldsets = BaseOrganizationAdmin.fieldsets + (
    ('CREDIS', {'fields': (('statut','secteur_fse'),('siret','naf'))}),
    )
    fieldsets = (
        (None, {
            'fields' : ('logo','title','subtitle',('birth','active',),
                        ('email','web'),'description','category',
                        'tags', # CREDIS utilise les tags
                        )
            }),
        ('Notes', {
            'classes': ('collapse',),
            'fields': ('notes',)
        })
    )  
    
admin.site.register(Organization, OrganizationAdmin) # BaseOrganization overridden here by Organization


class PersonAdmin(BasePersonAdmin):
    inlines = [
            ContactInline,
            OrgInline,
            SeeAlsoInline,
        ]
    fieldsets = (
        (None, {
            'fields' : (('first_name','last_name'),
                        ('location','location_display'), # CREDIS utilise coop-geo
                        'email',
                        'category'
                        ),
            }),
        ('Notes', {
            'classes': ('collapse',),
            'fields': ('structure','notes',)
        })
    )
    related_search_fields = {'location': ('label','adr1','adr2','zipcode','city'), }
    

admin.site.register(Person, PersonAdmin)


class ExchangeAdmin(BaseExchangeAdmin):
    fieldsets = ((None, {
            'fields' : ('etype',('permanent','expiration',),'title','description',
                        'tags',
                        'organization'
                       )
            }),)
    inlines = [
            PaymentInline,
            # LocatedInline, 
        ]

admin.site.register(Exchange, ExchangeAdmin)

#admin.site.register(PaymentModality)


from coop_cms.admin import ArticleAdmin as CmsArticleAdmin

class ArticleAdmin(CmsArticleAdmin):
    fieldsets = CmsArticleAdmin.fieldsets + (
        ('Misc', {'fields': ('author',)}),
    )

from coop_cms.settings import get_article_class
admin.site.unregister(get_article_class())
admin.site.register(get_article_class(), ArticleAdmin)




