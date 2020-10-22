import rdflib
from rdflib import BNode, Literal, URIRef
from rdflib.namespace import OWL, RDF, RDFS, SKOS, XSD, Namespace, NamespaceManager

rdf = RDF
rdfs = RDFS
bdr = Namespace("http://purl.bdrc.io/resource/")
bdo = Namespace("http://purl.bdrc.io/ontology/core/")
bdg = Namespace("http://purl.bdrc.io/graph/")
bda = Namespace("http://purl.bdrc.io/admindata/")
adm = Namespace("http://purl.bdrc.io/ontology/admin/")

nsm = NamespaceManager(rdflib.Graph())
nsm.bind("bdr", bdr)
nsm.bind("", bdo)
nsm.bind("bdg", bdg)
nsm.bind("bda", bda)
nsm.bind("adm", adm)
nsm.bind("rdf", rdf)
nsm.bind("rdfs", rdfs)
