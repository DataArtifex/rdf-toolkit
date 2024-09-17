from dataclasses import dataclass
from rdflib import ODRL2
from .rdf import RdfResource

@dataclass(kw_only=True)
class OdrlResource(RdfResource):
    def __post_init__(self):
        if hasattr(super(), '__post_init__'):
            super().__post_init__()
        self._namespace = ODRL2

@dataclass(kw_only=True)
class OdrlClass(OdrlResource):
    pass

@dataclass(kw_only=True)
class OdrlProperty(OdrlResource):
    pass

