
from typing import Optional
from dartfx.rdf import rdf

from dataclasses import dataclass, field

SPDX = "http://spdx.org/rdf/terms#"

@dataclass(kw_only=True)
class SpdxResource(rdf.RdfResource):
    def __post_init__(self):
        if hasattr(super(), '__post_init__'):
            super().__post_init__()
        self._namespace = SPDX

@dataclass(kw_only=True)
class SpdxClass(SpdxResource):
    pass
    
@dataclass(kw_only=True)
class SpdxProperty(SpdxResource):
    pass

@dataclass(kw_only=True)
class Checksum(SpdxClass):
    checksum: str
    algorithm: Optional[rdf.UriOrString] = field(default=None)

