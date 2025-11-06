"""Dublin Core Terms (DCTERMS) vocabulary using Pydantic RDF models.

This module provides Pydantic-based models for the Dublin Core Terms vocabulary,
allowing easy serialization to and from RDF formats.

References:
- https://www.dublincore.org/specifications/dublin-core/dcmi-terms/
- https://www.dublincore.org/specifications/dublin-core/collection-description/frequency/

"""

from datetime import datetime
from enum import Enum
from typing import Annotated, List, Optional, Union

from rdflib import Namespace, URIRef

from dartfx.rdf.pydantic_rdf import RdfBaseModel, RdfProperty


DCTERMS = Namespace("http://purl.org/dc/terms/")
FREQ = Namespace("http://purl.org/cld/freq/")


class DcmiFrequency(str, Enum):
    """DCMI Collection Description Frequency Vocabulary."""
    
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


class DctermsResource(RdfBaseModel):
    """Base class for Dublin Core Terms resources."""
    
    rdf_namespace = DCTERMS
    rdf_prefixes = {"dcterms": DCTERMS, "freq": FREQ}


class Agent(DctermsResource):
    """A resource that acts or has the power to act."""
    
    rdf_type = DCTERMS.Agent
    id: str
    name: Annotated[Optional[str], RdfProperty(DCTERMS.name)] = None


class DublinCoreRecord(DctermsResource):
    """A resource with Dublin Core metadata properties."""
    
    id: str
    title: Annotated[Optional[str], RdfProperty(DCTERMS.title, language="en")] = None
    description: Annotated[Optional[str], RdfProperty(DCTERMS.description, language="en")] = None
    creator: Annotated[Optional[Union[str, URIRef]], RdfProperty(DCTERMS.creator)] = None
    subject: Annotated[Optional[List[str]], RdfProperty(DCTERMS.subject)] = None
    publisher: Annotated[Optional[Union[str, URIRef]], RdfProperty(DCTERMS.publisher)] = None
    contributor: Annotated[Optional[List[Union[str, URIRef]]], RdfProperty(DCTERMS.contributor)] = None
    date: Annotated[Optional[datetime], RdfProperty(DCTERMS.date)] = None
    created: Annotated[Optional[datetime], RdfProperty(DCTERMS.created)] = None
    issued: Annotated[Optional[datetime], RdfProperty(DCTERMS.issued)] = None
    modified: Annotated[Optional[datetime], RdfProperty(DCTERMS.modified)] = None
    type: Annotated[Optional[Union[str, URIRef]], RdfProperty(DCTERMS.type)] = None
    format: Annotated[Optional[Union[str, URIRef]], RdfProperty(DCTERMS["format"])] = None
    identifier: Annotated[Optional[str], RdfProperty(DCTERMS.identifier)] = None
    source: Annotated[Optional[Union[str, URIRef]], RdfProperty(DCTERMS.source)] = None
    language: Annotated[Optional[Union[str, URIRef]], RdfProperty(DCTERMS.language)] = None
    relation: Annotated[Optional[List[Union[str, URIRef]]], RdfProperty(DCTERMS.relation)] = None
    coverage: Annotated[Optional[Union[str, URIRef]], RdfProperty(DCTERMS.coverage)] = None
    rights: Annotated[Optional[str], RdfProperty(DCTERMS.rights)] = None
    license: Annotated[Optional[Union[str, URIRef]], RdfProperty(DCTERMS.license)] = None
    accrual_periodicity: Annotated[Optional[Union[str, DcmiFrequency]], RdfProperty(DCTERMS.accrualPeriodicity)] = None


__all__ = ["DcmiFrequency", "DctermsResource", "Agent", "DublinCoreRecord"]
