"""

References:
- https://www.dublincore.org/specifications/dublin-core/dcmi-terms/

"""
from enum import Enum
from dartfx.rdf import rdf

from dataclasses import dataclass
from datetime import datetime
from typing import TypeAlias
from rdflib import DCTERMS

class DctermsResource(rdf.RdfResource):
    def __post_init__(self):
        if hasattr(super(), '__post_init__'):
            super().__post_init__()
        self._namespace = DCTERMS

class DctermsClass(DctermsResource):
    pass
    
class DctermsProperty(DctermsResource):
    pass

#
# VOCABULARIES
#

class DcmiFrequency(Enum):
    ANNUAL = "http://purl.org/cld/freq/annual"
    BIENNIAL = "http://purl.org/cld/freq/biennial"
    BIMONTHLY = "http://purl.org/cld/freq/bimonthly"
    BIWEEKLY = "http://purl.org/cld/freq/biweekly"
    CONTINUOUS = "http://purl.org/cld/freq/continuous"
    DAILY = "http://purl.org/cld/freq/daily"
    IRREGULAR = "http://purl.org/cld/freq/irregular"
    MONTHLY = "http://purl.org/cld/freq/monthly"
    QUARTERLY = "http://purl.org/cld/freq/quarterly"
    SEMIANNUAL = "http://purl.org/cld/freq/semiannual"
    SEMIMONTHLY = "http://purl.org/cld/freq/semimonthly"
    SEMIWEEKLY = "http://purl.org/cld/freq/semiweekly"
    THREE_TIMES_A_MONTH = "http://purl.org/cld/freq/threeTimesAMonth"
    THREE_TIMES_A_WEEK = "http://purl.org/cld/freq/threeTimesAWeek"
    TRIENNIAL = "http://purl.org/cld/freq/triennial"
    WEEKLY = "http://purl.org/cld/freq/weekly"

@dataclass(kw_only=True)
class AccrualPeriodicity(rdf.UriOrString):
    """Accrual Periodicity
       
    The frequency with which items are added to a collection.
    
    Recommended practice is to use a value from the Collection Description Frequency Vocabulary [DCMI-COLLFREQ].
    
    See also:
    - https://www.dublincore.org/specifications/dublin-core/dcmi-terms/#accrualPeriodicity
    - https://www.dublincore.org/specifications/dublin-core/collection-description/frequency/

    """
    pass

@dataclass(kw_only=True)
class AccessRights(DctermsProperty, rdf.UriOrString):
    pass

@dataclass(kw_only=True)
class ConformsTo(DctermsProperty, rdf.UriOrString):
    pass    

@dataclass(kw_only=True)
class Creator(DctermsProperty, rdf.UriOrString):
    pass

@dataclass(kw_only=True)
class Description(DctermsProperty,rdf.RdfString):
    pass

@dataclass(kw_only=True)
class Identifier(DctermsProperty,rdf.RdfString):
    pass

Issued: TypeAlias = datetime

@dataclass(kw_only=True)
class Language(DctermsProperty, rdf.UriOrString):
    pass

@dataclass(kw_only=True)
class License(DctermsProperty, rdf.UriOrString):
    pass

@dataclass(kw_only=True)
class Location(DctermsProperty, rdf.RdfString):
    pass    

Modified: TypeAlias = datetime

@dataclass(kw_only=True)
class Publisher(DctermsProperty, rdf.UriOrString):
    pass    

@dataclass(kw_only=True)
class PeriodOfTime(DctermsProperty):
    pass

@dataclass(kw_only=True)
class Title(DctermsProperty,rdf.RdfString):
    pass

@dataclass(kw_only=True)
class Type(DctermsProperty, rdf.UriOrString):
    pass    

@dataclass(kw_only=True)
class Relation(DctermsProperty, rdf.UriOrString):
    """A related resource.

    Recommended practice is to identify the related resource by means of a URI. If this is not possible or feasible, a string conforming to a formal identification system may be provided.
    
    """
    pass

@dataclass(kw_only=True)
class Rights(DctermsProperty, rdf.UriOrString):
    pass

    
@dataclass(kw_only=True)
class Spatial(DctermsProperty,rdf.UriOrString):
    pass
