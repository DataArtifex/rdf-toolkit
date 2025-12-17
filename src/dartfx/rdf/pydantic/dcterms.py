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

from ._base import RdfBaseModel, RdfProperty


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


    valid: Annotated[Optional[datetime], RdfProperty(DCTERMS.valid)] = None


class BibliographicResource(DctermsResource):
    """A bibliographic resource."""
    rdf_type = DCTERMS.BibliographicResource


class FileFormat(DctermsResource):
    """A file format."""
    rdf_type = DCTERMS.FileFormat


class Frequency(DctermsResource):
    """A rate of occurrence."""
    rdf_type = DCTERMS.Frequency


class Jurisdiction(DctermsResource):
    """The extent or range of judicial, law enforcement, or other authority."""
    rdf_type = DCTERMS.Jurisdiction


class LicenseDocument(DctermsResource):
    """A legal document giving official permission to do something with a Resource."""
    rdf_type = DCTERMS.LicenseDocument


class Location(DctermsResource):
    """A spatial region or named place."""
    rdf_type = DCTERMS.Location


class LocationPeriodOrJurisdiction(DctermsResource):
    """A location, period of time, or jurisdiction."""
    rdf_type = DCTERMS.LocationPeriodOrJurisdiction


class MediaType(DctermsResource):
    """A file format or physical medium."""
    rdf_type = DCTERMS.MediaType


class MediaTypeOrExtent(DctermsResource):
    """A media type or extent."""
    rdf_type = DCTERMS.MediaTypeOrExtent


class MethodOfAccrual(DctermsResource):
    """A method by which items are added to a collection."""
    rdf_type = DCTERMS.MethodOfAccrual


class MethodOfInstruction(DctermsResource):
    """A process that is used to engender knowledge, attitudes, and skills."""
    rdf_type = DCTERMS.MethodOfInstruction


class PeriodOfTime(DctermsResource):
    """An interval of time that is named or defined by its start and end dates."""
    rdf_type = DCTERMS.PeriodOfTime


class PhysicalMedium(DctermsResource):
    """A physical material or carrier."""
    rdf_type = DCTERMS.PhysicalMedium


class PhysicalResource(DctermsResource):
    """A material thing."""
    rdf_type = DCTERMS.PhysicalResource


class Policy(DctermsResource):
    """A plan or course of action by an authority, intended to influence and determine decisions, actions, and other matters."""
    rdf_type = DCTERMS.Policy


class ProvenanceStatement(DctermsResource):
    """A statement of any changes in ownership and custody of a resource since its creation that are significant for its authenticity, integrity, and interpretation."""
    rdf_type = DCTERMS.ProvenanceStatement


class RightsStatement(DctermsResource):
    """A statement about the intellectual property rights (IPR) held in or over a Resource, a legal document giving official permission to do something with a resource, or a statement about access rights."""
    rdf_type = DCTERMS.RightsStatement


class SizeOrDuration(DctermsResource):
    """A dimension or extent, or a time taken to play or execute."""
    rdf_type = DCTERMS.SizeOrDuration


class Standard(DctermsResource):
    """A basis for comparison; a reference point against which other things can be evaluated."""
    rdf_type = DCTERMS.Standard


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
    
    # New properties
    abstract: Annotated[Optional[str], RdfProperty(DCTERMS.abstract)] = None
    access_rights: Annotated[Optional[Union[str, URIRef, RightsStatement]], RdfProperty(DCTERMS.accessRights)] = None
    alternative: Annotated[Optional[str], RdfProperty(DCTERMS.alternative)] = None
    audience: Annotated[Optional[Union[str, URIRef, Agent]], RdfProperty(DCTERMS.audience)] = None
    available: Annotated[Optional[datetime], RdfProperty(DCTERMS.available)] = None
    bibliographic_citation: Annotated[Optional[str], RdfProperty(DCTERMS.bibliographicCitation)] = None
    conforms_to: Annotated[Optional[Union[str, URIRef, Standard]], RdfProperty(DCTERMS.conformsTo)] = None
    date_accepted: Annotated[Optional[datetime], RdfProperty(DCTERMS.dateAccepted)] = None
    date_copyrighted: Annotated[Optional[datetime], RdfProperty(DCTERMS.dateCopyrighted)] = None
    date_submitted: Annotated[Optional[datetime], RdfProperty(DCTERMS.dateSubmitted)] = None
    education_level: Annotated[Optional[Union[str, URIRef]], RdfProperty(DCTERMS.educationLevel)] = None
    extent: Annotated[Optional[Union[str, URIRef, SizeOrDuration]], RdfProperty(DCTERMS.extent)] = None
    has_format: Annotated[Optional[Union[str, URIRef]], RdfProperty(DCTERMS.hasFormat)] = None
    has_part: Annotated[Optional[Union[str, URIRef]], RdfProperty(DCTERMS.hasPart)] = None
    has_version: Annotated[Optional[Union[str, URIRef]], RdfProperty(DCTERMS.hasVersion)] = None
    instructional_method: Annotated[Optional[Union[str, URIRef, MethodOfInstruction]], RdfProperty(DCTERMS.instructionalMethod)] = None
    is_format_of: Annotated[Optional[Union[str, URIRef]], RdfProperty(DCTERMS.isFormatOf)] = None
    is_part_of: Annotated[Optional[Union[str, URIRef]], RdfProperty(DCTERMS.isPartOf)] = None
    is_referenced_by: Annotated[Optional[Union[str, URIRef]], RdfProperty(DCTERMS.isReferencedBy)] = None
    is_replaced_by: Annotated[Optional[Union[str, URIRef]], RdfProperty(DCTERMS.isReplacedBy)] = None
    is_required_by: Annotated[Optional[Union[str, URIRef]], RdfProperty(DCTERMS.isRequiredBy)] = None
    is_version_of: Annotated[Optional[Union[str, URIRef]], RdfProperty(DCTERMS.isVersionOf)] = None
    mediator: Annotated[Optional[Union[str, URIRef, Agent]], RdfProperty(DCTERMS.mediator)] = None
    medium: Annotated[Optional[Union[str, URIRef, PhysicalMedium, MediaType]], RdfProperty(DCTERMS.medium)] = None
    references: Annotated[Optional[Union[str, URIRef]], RdfProperty(DCTERMS.references)] = None
    replaces: Annotated[Optional[Union[str, URIRef]], RdfProperty(DCTERMS.replaces)] = None
    requires: Annotated[Optional[Union[str, URIRef]], RdfProperty(DCTERMS.requires)] = None
    spatial: Annotated[Optional[Union[str, URIRef, Location]], RdfProperty(DCTERMS.spatial)] = None
    table_of_contents: Annotated[Optional[str], RdfProperty(DCTERMS.tableOfContents)] = None
    temporal: Annotated[Optional[Union[str, URIRef, PeriodOfTime]], RdfProperty(DCTERMS.temporal)] = None
    valid: Annotated[Optional[datetime], RdfProperty(DCTERMS.valid)] = None



__all__ = [
    "DcmiFrequency",
    "DctermsResource",
    "Agent",
    "DublinCoreRecord",
    "BibliographicResource",
    "FileFormat",
    "Frequency",
    "Jurisdiction",
    "LicenseDocument",
    "Location",
    "LocationPeriodOrJurisdiction",
    "MediaType",
    "MediaTypeOrExtent",
    "MethodOfAccrual",
    "MethodOfInstruction",
    "PeriodOfTime",
    "PhysicalMedium",
    "PhysicalResource",
    "Policy",
    "ProvenanceStatement",
    "RightsStatement",
    "SizeOrDuration",
    "Standard",
]

