"""Dublin Core Terms (DCTERMS) vocabulary using Pydantic RDF models.

This module provides Pydantic-based models for the Dublin Core Terms vocabulary,
allowing easy serialization to and from RDF formats.

References:
- https://www.dublincore.org/specifications/dublin-core/dcmi-terms/
- https://www.dublincore.org/specifications/dublin-core/collection-description/frequency/

"""

from datetime import datetime
from enum import StrEnum
from typing import Annotated

from rdflib import Namespace, URIRef

from ._base import LocalizedStr, RdfBaseModel, RdfProperty

DCTERMS = Namespace("http://purl.org/dc/terms/")
FREQ = Namespace("http://purl.org/cld/freq/")


class DcmiFrequency(StrEnum):
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
    name: Annotated[
        LocalizedStr | None,
        RdfProperty(DCTERMS.name),
    ] = None

    valid: Annotated[datetime | list[datetime] | None, RdfProperty(DCTERMS.valid)] = None


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
    """A plan or course of action by an authority.

    Intended to influence and determine decisions, actions, and other matters.
    """

    rdf_type = DCTERMS.Policy


class ProvenanceStatement(DctermsResource):
    """A statement of changes in ownership and custody of a resource.

    Includes changes since creation that are significant for authenticity, integrity, and interpretation.
    """

    rdf_type = DCTERMS.ProvenanceStatement


class RightsStatement(DctermsResource):
    """A statement about intellectual property rights or permissions.

    This includes IPR held in or over a Resource, legal documents giving official permission to do
    something with a resource, or statements about access rights.
    """

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
    title: Annotated[
        LocalizedStr | None,
        RdfProperty(DCTERMS.title),
    ] = None
    description: Annotated[
        LocalizedStr | None,
        RdfProperty(DCTERMS.description),
    ] = None
    creator: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(DCTERMS.creator)] = None
    subject: Annotated[
        LocalizedStr | None,
        RdfProperty(DCTERMS.subject),
    ] = None
    publisher: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(DCTERMS.publisher)] = None
    contributor: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(DCTERMS.contributor)] = None
    date: Annotated[datetime | list[datetime] | None, RdfProperty(DCTERMS.date)] = None
    created: Annotated[datetime | list[datetime] | None, RdfProperty(DCTERMS.created)] = None
    issued: Annotated[datetime | list[datetime] | None, RdfProperty(DCTERMS.issued)] = None
    modified: Annotated[datetime | list[datetime] | None, RdfProperty(DCTERMS.modified)] = None
    type: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(DCTERMS.type)] = None
    format: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(DCTERMS["format"])] = None
    identifier: Annotated[str | list[str] | None, RdfProperty(DCTERMS.identifier)] = None
    source: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(DCTERMS.source)] = None
    language: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(DCTERMS.language)] = None
    relation: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(DCTERMS.relation)] = None
    coverage: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(DCTERMS.coverage)] = None
    rights: Annotated[
        LocalizedStr | None,
        RdfProperty(DCTERMS.rights),
    ] = None
    license: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(DCTERMS.license)] = None
    accrual_periodicity: Annotated[
        str | DcmiFrequency | list[str | DcmiFrequency] | None,
        RdfProperty(DCTERMS.accrualPeriodicity),
    ] = None

    # New properties
    abstract: Annotated[
        LocalizedStr | None,
        RdfProperty(DCTERMS.abstract),
    ] = None
    access_rights: Annotated[
        str | URIRef | RightsStatement | list[str | URIRef | RightsStatement] | None,
        RdfProperty(DCTERMS.accessRights),
    ] = None
    alternative: Annotated[
        LocalizedStr | None,
        RdfProperty(DCTERMS.alternative),
    ] = None
    audience: Annotated[
        str | URIRef | Agent | list[str | URIRef | Agent] | None,
        RdfProperty(DCTERMS.audience),
    ] = None
    available: Annotated[datetime | list[datetime] | None, RdfProperty(DCTERMS.available)] = None
    bibliographic_citation: Annotated[
        LocalizedStr | None,
        RdfProperty(DCTERMS.bibliographicCitation),
    ] = None
    conforms_to: Annotated[
        str | URIRef | Standard | list[str | URIRef | Standard] | None,
        RdfProperty(DCTERMS.conformsTo),
    ] = None
    date_accepted: Annotated[datetime | list[datetime] | None, RdfProperty(DCTERMS.dateAccepted)] = None
    date_copyrighted: Annotated[datetime | list[datetime] | None, RdfProperty(DCTERMS.dateCopyrighted)] = None
    date_submitted: Annotated[datetime | list[datetime] | None, RdfProperty(DCTERMS.dateSubmitted)] = None
    education_level: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(DCTERMS.educationLevel)] = None
    extent: Annotated[
        str | URIRef | SizeOrDuration | list[str | URIRef | SizeOrDuration] | None,
        RdfProperty(DCTERMS.extent),
    ] = None
    has_format: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(DCTERMS.hasFormat)] = None
    has_part: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(DCTERMS.hasPart)] = None
    has_version: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(DCTERMS.hasVersion)] = None
    instructional_method: Annotated[
        str | URIRef | MethodOfInstruction | list[str | URIRef | MethodOfInstruction] | None,
        RdfProperty(DCTERMS.instructionalMethod),
    ] = None
    is_format_of: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(DCTERMS.isFormatOf)] = None
    is_part_of: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(DCTERMS.isPartOf)] = None
    is_referenced_by: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(DCTERMS.isReferencedBy)] = None
    is_replaced_by: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(DCTERMS.isReplacedBy)] = None
    is_required_by: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(DCTERMS.isRequiredBy)] = None
    is_version_of: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(DCTERMS.isVersionOf)] = None
    mediator: Annotated[str | URIRef | Agent | list[str | URIRef | Agent] | None, RdfProperty(DCTERMS.mediator)] = None
    medium: Annotated[
        str | URIRef | PhysicalMedium | MediaType | list[str | URIRef | PhysicalMedium | MediaType] | None,
        RdfProperty(DCTERMS.medium),
    ] = None
    references: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(DCTERMS.references)] = None
    replaces: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(DCTERMS.replaces)] = None
    requires: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(DCTERMS.requires)] = None
    spatial: Annotated[
        str | URIRef | Location | list[str | URIRef | Location] | None,
        RdfProperty(DCTERMS.spatial),
    ] = None
    table_of_contents: Annotated[
        LocalizedStr | None,
        RdfProperty(DCTERMS.tableOfContents),
    ] = None
    temporal: Annotated[
        str | URIRef | PeriodOfTime | list[str | URIRef | PeriodOfTime] | None,
        RdfProperty(DCTERMS.temporal),
    ] = None
    valid: Annotated[datetime | list[datetime] | None, RdfProperty(DCTERMS.valid)] = None


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
