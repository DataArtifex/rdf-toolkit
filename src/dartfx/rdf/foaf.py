from .rdf import RdfResource, UriOrString

from dataclasses import dataclass
from rdflib import FOAF

@dataclass(kw_only=True)
class FoafResource(RdfResource):
    def __post_init__(self):
        if hasattr(super(), '__post_init__'):
            super().__post_init__()
        self._namespace = FOAF

@dataclass(kw_only=True)
class FoafClass(FoafResource):
    pass
    
@dataclass(kw_only=True)
class FoafProperty(FoafResource):
    pass

@dataclass(kw_only=True)
class Agent(FoafClass):
    pass

@dataclass(kw_only=True)
class Organization(Agent):
    pass

@dataclass(kw_only=True)
class Person(Agent):
    pass

@dataclass(kw_only=True)
class Homepage(FoafProperty, UriOrString):
    pass