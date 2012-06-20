from rdflib import Namespace

DEFAULT_RDF_NAMESPACES = {
 'ess':  u'http://ns.economie-solidaire.fr/ess#',
 'dct': u'http://purl.org/dc/terms/',
 'org': u'http://www.w3.org/ns/org#',
 'ctag': u'http://commontag.org/ns#',
 'foaf': u'http://xmlns.com/foaf/0.1/',
 'locn': u'http://www.w3.org/ns/locn#',
 'skos': u'http://www.w3.org/2004/02/skos/core#',
 'legal': u'http://www.w3.org/ns/legal#',
 'vcard': u'http://www.w3.org/2006/vcard/ns#',
 'xsd': 'http://www.w3.org/2001/XMLSchema#',
 'geofr': u'http://rdf.insee.fr/geo/',
 'skosxl': u'http://www.w3.org/2008/05/skos-xl#',
 'gr': u'http://purl.org/goodrelations/v1#',
 'event': u'http://purl.org/NET/c4dm/event.owl#',
 'sioc': u'http://rdfs.org/sioc/ns#',
 'opens': u'http://rdf.opensahara.com/type/geo/',
 'person': u'http://www.w3.org/ns/person#',
 'schema': u'http://schema.org/',
 'rss': u'http://purl.org/net/rss1.1#',
 'ov': u'http://open.vocab.org/terms/'
 }


 # Useful stuffs
NS_D2RQ = Namespace('http://www.wiwiss.fu-berlin.de/suhl/bizer/D2RQ/0.1#')
NS_LEGAL = Namespace(DEFAULT_RDF_NAMESPACES['legal'])
NS_ESS = Namespace(DEFAULT_RDF_NAMESPACES['ess'])
NS_SKOS = Namespace(DEFAULT_RDF_NAMESPACES['skos'])
NS_OV = Namespace(DEFAULT_RDF_NAMESPACES['ov'])
NS_RDFS = Namespace(u'http://www.w3.org/2000/01/rdf-schema#')
