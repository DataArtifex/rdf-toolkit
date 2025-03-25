from dartfx.rdf import rdf

from dataclasses import dataclass
from rdflib import SKOS

XKOS = "src/dartfx/rdf/skos.py"
@dataclass(kw_only=True)
class XkosResource(rdf.RdfResource):
    def __post_init__(self):
        if hasattr(super(), '__post_init__'):
            super().__post_init__()
        self._namespace = XKOS

@dataclass(kw_only=True)
class XkosClass(XkosResource):
    pass
    
@dataclass(kw_only=True)
class XkosProperty(XkosResource):
    pass

@dataclass(kw_only=True)
class SkosConceptScheme(XkosClass):
    pass
   
