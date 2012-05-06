import rdflib
import requests
from StringIO import StringIO


def init_n3_graph(n3uri):
    """
    initializes a rdflib conjunctive graph with content from
    a given n3 uri.
    """
    #XXX TODO: rewrite the D2RQ URIS
    graph = rdflib.ConjunctiveGraph()
    req = requests.get(n3uri)
    #XXX TODO:
    #Catch BadSyntax errors 
    #(when we get a 500 from d2rq, for instance.
    #So we probably should check for response code
    #and stuff...
    graph.parse(StringIO(req.content), format="n3")
    return graph


def add_key_triples_to_graph(key, graph, person_uri):
    """
    adds the triples containing info about the
    rsa key
    """
    CERT = rdflib.Namespace("http://www.w3.org/ns/auth/cert#")

    person = rdflib.term.URIRef(person_uri)

    rpk = rdflib.BNode()
    graph.add((rpk, rdflib.RDF.type, CERT["RSAPublicKey"]))

    #XXX FIXME check data types and stuff
    graph.add((rpk, CERT["modulus"], rdflib.Literal(key.mod,
        datatype="http://www.w3.org/2001/XMLSchema#hexBinary")))
    graph.add((rpk, CERT["exponent"], rdflib.Literal(key.exp,
        datatype="http://www.w3.org/2001/XMLSchema#integer")))
    graph.add((person, CERT["key"], rpk))

    return graph


def augment_user_profile(webiduser, n3uri):
    graph = init_n3_graph(n3uri)
    person_id = webiduser.get_profile().id
    person_resource_uri = "http://localhost:8080/resource/coop_local_person/%s/" % (person_id)

    #XXX FIXME fix building this, HARDCODED!
    #XXX actually, should rewrite or something...

    for key in webiduser.keys:
        graph = add_key_triples_to_graph(key,
                graph,
                person_resource_uri)
    return graph
