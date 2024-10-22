# -*- coding:utf-8 -*-

# Not used: to set this variable here, we need to import Site
PUSH_HUB = ''
SUBHUB_MAINTENANCE_AUTO = False

BASE_COOP_LOCAL_MODELS = [
    ('coop_geo', [
        u'Location',
        u'Area',
    ]),
    ('coop.rdf', [
        u'DeletedURI',
    ]),
    ('coop_cms', [
        u'Article',
        u'NavTree',
    ]),
    ('coop.link', [
        u'LinkProperty',
        u'Link',
    ]),
    ('coop_tag', [
        u'Tag',
        u'TaggedItem',
    ]),
    ('coop.agenda', [
        u'Calendar',
        u'Dated',
        u'Event',
        u'EventCategory',
        u'Occurrence',
        u'GenericDate',
    ]),
    ('coop.doc', [
        u'ResourceCategory',
        u'DocResource',
        u'Attachment',
    ]),
    ('coop.person', [
        u'Person',
        u'PersonCategory',
    ]),
    ('coop.org', [
        u'ContactMedium',
        u'Contact',
        u'Engagement',
        u'Role',
        u'RoleCategory',
        u'OrgRelationType',
        u'Relation',
        u'OrganizationCategory',
        u'Organization',
    ]),
    ('coop.project', [
        u'ProjectCategory',
        u'ProjectSupport',
        u'ProjectMember',
        u'Project',
    ]),
    ('coop.exchange', [
        u'ExchangeMethod',
        u'Product',
        u'Exchange',
    ]),
    ('coop.mailing', [
        u'MailingList',
        u'Subscription',
        u'Newsletter',
        u'NewsElement',
        u'NewsletterSending',
    ]),
    ('coop.prefs', [
        u'SitePrefs',
    ]),
]


from rdflib import Namespace


class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


def transform_dict(dict):
    for key, value in dict.items():
        dict[key] = Namespace(value)
    return dict


RDF_NAMESPACES = {'ctag': u'http://commontag.org/ns#',
                  'd2rq': u'http://www.wiwiss.fu-berlin.de/suhl/bizer/D2RQ/0.1#',
                  'dct': u'http://purl.org/dc/terms/',
                  'dce': u'http://purl.org/dc/elements/1.1/',
                  'dcmi': u'http://purl.org/dc/dcmitype/',
                  'ess':  u'http://ns.economie-solidaire.fr/ess#',
                  'event': u'http://purl.org/NET/c4dm/event.owl#',
                  'foaf': u'http://xmlns.com/foaf/0.1/',
                  'geofr': u'http://rdf.insee.fr/geo/',
                  'gr': u'http://purl.org/goodrelations/v1#',
                  'legal': u'http://www.w3.org/ns/legal#',
                  'locn': u'http://www.w3.org/ns/locn#',
                  'opens': u'http://rdf.opensahara.com/type/geo/',
                  'org': u'http://www.w3.org/ns/org#',
                  'ov': u'http://open.vocab.org/terms/',
                  'person': u'http://www.w3.org/ns/person#',
                  'rdfs': u'http://www.w3.org/2000/01/rdf-schema#',
                  'rdf': u'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                  'rss': u'http://purl.org/net/rss1.1#',
                  'schema': u'http://schema.org/',
                  'sioc': u'http://rdfs.org/sioc/ns#',
                  'skos': u'http://www.w3.org/2004/02/skos/core#',
                  'skosxl': u'http://www.w3.org/2008/05/skos-xl#',
                  'vcal': u'http://www.w3.org/2002/12/cal/icaltzd#',
                  'vcard': u'http://www.w3.org/2006/vcard/ns#',
                  'xsd': 'http://www.w3.org/2001/XMLSchema#',
                  }


# NS = AttributeDict( transform_dict(RDF_NAMESPACES).items() )

