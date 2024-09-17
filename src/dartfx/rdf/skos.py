from dartfx.rdf import rdf

from dataclasses import dataclass
from rdflib import SKOS

@dataclass(kw_only=True)
class SkosResource(rdf.RdfResource):
    def __post_init__(self):
        if hasattr(super(), '__post_init__'):
            super().__post_init__()
        self._namespace = SKOS

@dataclass(kw_only=True)
class SkosClass(SkosResource):
    pass
    
@dataclass(kw_only=True)
class SkosProperty(SkosResource):
    pass

@dataclass(kw_only=True)
class SkosConceptScheme(SkosClass):
    pass
   
@dataclass(kw_only=True)    
class SkosConcept(SkosClass):
    pass
