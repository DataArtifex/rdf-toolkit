from dartfx.rdf import rdf

from dataclasses import dataclass


VCARD = "http://www.w3.org/2006/vcard/ns#"

@dataclass(kw_only=True)
class VcardResource(rdf.RdfResource):
    def __post_init__(self):
        if hasattr(super(), '__post_init__'):
            super().__post_init__()
        self._namespace = VCARD

@dataclass(kw_only=True)
class VcardClass(VcardResource):
    pass

@dataclass(kw_only=True)
class VcardProperty(VcardResource):
    pass

