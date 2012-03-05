# premier essai extraction des CC de dbpedia.inria.fr

def cc_region(region):
    return u"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dbpo: <http://dbpedia.org/ontology/>
    PREFIX dbfr: <http://fr.dbpedia.org/resource/>
    PREFIX dbpropfr: <http://fr.dbpedia.org/property/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    select distinct ?cc ?cclabel where {
        ?v dbpropfr:région """+region+""" ;
           a dbpo:PopulatedPlace ;
           dbpropfr:intercomm ?cc .
        ?cc rdfs:label ?cclabel .
        OPTIONAL {?cc dbpo:wikiPageRedirects ?redir . }
        FILTER (!bound(?redir))
    }LIMIT 1
    """

def list_communes(uri):
    return u"""
    PREFIX dbpo: <http://dbpedia.org/ontology/>
    PREFIX dbfr: <http://fr.dbpedia.org/resource/>
    PREFIX dbpropfr: <http://fr.dbpedia.org/property/>
    select ?insee where {
        ?v a dbpo:PopulatedPlace ;
           dbpropfr:intercomm <"""+uri+"""> ;
           dbpropfr:insee ?insee .
        OPTIONAL {?v dbpo:wikiPageRedirects ?redir . }
        FILTER (!bound(?redir))
    }
    """

from SPARQLWrapper import SPARQLWrapper,JSON, XML

def dbpedia(query):
    sparql = SPARQLWrapper('http://dbpedia.inria.fr/sparql')
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results["results"]["bindings"]

ccom = []

for result in dbpedia(cc_region(u'dbfr:Auvergne')):
    communes = []
    for c in dbpedia(list_communes(result["cc"]["value"])) :
        communes.append(c["insee"]["value"])
    cc = {  'label': result["cclabel"]["value"],
            'uri': result["cc"]["value"],
            'communes':communes}
    ccom.append(cc)



