
from abc import ABC, abstractmethod
import uuid

from rdflib import Graph
from .rdf import Uri

def get_rdf_graph_statistics(g: Graph):
    stats = {}
    # count triples
    query = """
    SELECT (COUNT(*) AS ?n)
    WHERE {
        ?s ?p ?o
    }
    """
    for row in g.query(query):
        stats["n_triples"] = int(str(row.n))

    # count type instances
    query = """
    SELECT ?type (COUNT(?instance) AS ?n)
    WHERE {
        ?instance a ?type .
    }
    GROUP BY ?type
    ORDER BY ?type
    """
    stats["types"] = {}
    for row in g.query(query):
        type = str(g.namespace_manager.qname(row.type))
        stats["types"][type] = {}
        stats["types"][type]["count"] = int(str(row.n))

    # count type properties instances
    query = """
    SELECT ?property (COUNT(?property) AS ?n)
    WHERE {
    ?resource a ?type .
    ?resource ?property ?value .
    }
    GROUP BY ?property
    ORDER BY ?property
    """
    stats["properties"] = {}
    for row in g.query(query):
        property = str(g.namespace_manager.qname(row.property))
        stats["properties"][property] = {}
        stats["properties"][property]["count"] = int(str(row.n))


#
# URI Generators
#

class UriGenerator(ABC):
    
    @abstractmethod
    def get_string(self, *args, **kwargs) -> str:
        pass    
    
    @abstractmethod
    def get_uri(self, *args, **kwargs) -> Uri:
        pass
    
class UuidUrnGenerator():
    
    def get_string(self, *args, **kwargs) -> str:
        return uuid.uuid4().urn
    
    def get_uri(self, *args, **kwargs) -> Uri:
        return Uri(value=self.get_string())
        
class UrlUriGenerator(UriGenerator):
    base_url: str
    
    def __init__(self, base_url: str = "http://example.org"):
        self.base_url = base_url
        
    def get_string(self, ids: str|list[str], *args, **kwargs) -> str:
        if isinstance(ids, str):
            return f"{self.base_url}/{ids}"
        else:
            return [f"{self.base_url}/{i}" for i in ids]        

class UrnUriGenerator(UriGenerator):
    base_urn: str
    
    def __init__(self, base_urn: str = "urn:foo"):
        self.base_url = base_urn
    