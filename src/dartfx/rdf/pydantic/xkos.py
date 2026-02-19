"""XKOS (Extended Knowledge Organization System) vocabulary using Pydantic RDF models.

This module provides Pydantic-based models for the XKOS vocabulary,
which extends SKOS for statistical classifications.

References:
- http://rdf-vocabulary.ddialliance.org/xkos.html
- https://rdf-vocabulary.ddialliance.org/xkos

"""

from __future__ import annotations

from typing import Annotated, ClassVar

from rdflib import SKOS, Namespace, URIRef

from ._base import RdfBaseModel, RdfProperty

# XKOS namespace
XKOS = Namespace("http://rdf-vocabulary.ddialliance.org/xkos#")


class XkosResource(RdfBaseModel):
    """Base class for XKOS resources."""

    rdf_namespace: ClassVar = XKOS
    rdf_prefixes: ClassVar = {"xkos": XKOS, "skos": SKOS}  # type: ignore[dict-item]


class ClassificationLevel(XkosResource):
    """An XKOS Classification Level - a level in a statistical classification."""

    rdf_type: ClassVar[str] = str(XKOS.ClassificationLevel)

    # Level properties
    depth: Annotated[list[int] | None, RdfProperty(XKOS.depth)] = None
    notations_equal: Annotated[list[str] | None, RdfProperty(XKOS.notationsEqual)] = None
    organizes: Annotated[list[str | URIRef] | None, RdfProperty(XKOS.organizes)] = None
    covers: Annotated[list[str | URIRef] | None, RdfProperty(XKOS.covers)] = None
    covers_exhaustively: Annotated[list[str | URIRef] | None, RdfProperty(XKOS.coversExhaustively)] = None
    covers_mutually_exclusively: Annotated[list[str | URIRef] | None, RdfProperty(XKOS.coversMutuallyExclusively)] = (
        None
    )

    # Textual properties
    organized_by: Annotated[list[str | URIRef] | None, RdfProperty(XKOS.organizedBy)] = None
    notation_pattern: Annotated[list[str] | None, RdfProperty(XKOS.notationPattern)] = None
    max_length: Annotated[list[int] | None, RdfProperty(XKOS.maxLength)] = None

    # Labels (from SKOS)
    pref_label: Annotated[list[str] | None, RdfProperty(SKOS.prefLabel)] = None
    alt_label: Annotated[list[str] | None, RdfProperty(SKOS.altLabel)] = None

    # Notes
    note: Annotated[list[str] | None, RdfProperty(SKOS.note)] = None


class ConceptAssociation(XkosResource):
    """An XKOS Concept Association - a relationship between concepts in different classifications."""

    rdf_type: ClassVar[str] = str(XKOS.ConceptAssociation)

    # Source and target
    source_concept: Annotated[list[str | URIRef] | None, RdfProperty(XKOS.sourceConcept)] = None
    target_concept: Annotated[list[str | URIRef] | None, RdfProperty(XKOS.targetConcept)] = None


class Correspondence(XkosResource):
    """An XKOS Correspondence - a mapping between two classifications."""

    rdf_type: ClassVar[str] = str(XKOS.Correspondence)

    # Source and target classifications
    compares: Annotated[list[str | URIRef] | None, RdfProperty(XKOS.compares)] = None

    # Labels
    pref_label: Annotated[list[str] | None, RdfProperty(SKOS.prefLabel)] = None
    alt_label: Annotated[list[str] | None, RdfProperty(SKOS.altLabel)] = None

    # Definition
    definition: Annotated[list[str] | None, RdfProperty(SKOS.definition)] = None

    # Associations
    made_of: Annotated[list[str | URIRef | ConceptAssociation] | None, RdfProperty(XKOS.madeOf)] = None


class ExplanatoryNote(XkosResource):
    """An XKOS Explanatory Note - additional documentation for a concept."""

    rdf_type: ClassVar[str] = str(XKOS.ExplanatoryNote)

    # Descriptive text
    plain_text: Annotated[list[str] | None, RdfProperty(XKOS.plainText)] = None


# Extended SKOS Concept for statistical classifications
class StatisticalConcept(XkosResource):
    """A SKOS Concept with XKOS extensions for statistical classifications."""

    rdf_type: ClassVar[str] = str(SKOS.Concept)

    # SKOS properties
    pref_label: Annotated[list[str] | None, RdfProperty(SKOS.prefLabel)] = None
    alt_label: Annotated[list[str] | None, RdfProperty(SKOS.altLabel)] = None
    hidden_label: Annotated[list[str] | None, RdfProperty(SKOS.hiddenLabel)] = None
    notation: Annotated[list[str] | None, RdfProperty(SKOS.notation)] = None
    definition: Annotated[list[str] | None, RdfProperty(SKOS.definition)] = None

    # SKOS semantic relations
    broader: Annotated[list[str | URIRef | StatisticalConcept] | None, RdfProperty(SKOS.broader)] = None
    narrower: Annotated[list[str | URIRef | StatisticalConcept] | None, RdfProperty(SKOS.narrower)] = None
    related: Annotated[list[str | URIRef | StatisticalConcept] | None, RdfProperty(SKOS.related)] = None

    # Concept scheme
    in_scheme: Annotated[list[str | URIRef] | None, RdfProperty(SKOS.inScheme)] = None
    top_concept_of: Annotated[list[str | URIRef] | None, RdfProperty(SKOS.topConceptOf)] = None

    # XKOS extensions
    core_content_note: Annotated[list[str] | None, RdfProperty(XKOS.coreContentNote)] = None
    additional_content_note: Annotated[list[str] | None, RdfProperty(XKOS.additionalContentNote)] = None
    exclusion_note: Annotated[list[str] | None, RdfProperty(XKOS.exclusionNote)] = None
    inclusion_note: Annotated[list[str] | None, RdfProperty(XKOS.inclusionNote)] = None

    # Causal relationships
    causal: Annotated[list[str | URIRef | StatisticalConcept] | None, RdfProperty(XKOS.causal)] = None
    causes: Annotated[list[str | URIRef | StatisticalConcept] | None, RdfProperty(XKOS.causes)] = None
    caused_by: Annotated[list[str | URIRef | StatisticalConcept] | None, RdfProperty(XKOS.causedBy)] = None

    # Sequential relationships
    sequential: Annotated[list[str | URIRef | StatisticalConcept] | None, RdfProperty(XKOS.sequential)] = None
    precedes: Annotated[list[str | URIRef | StatisticalConcept] | None, RdfProperty(XKOS.precedes)] = None
    follows: Annotated[list[str | URIRef | StatisticalConcept] | None, RdfProperty(XKOS.follows)] = None

    # Temporal relationships
    temporal: Annotated[list[str | URIRef | StatisticalConcept] | None, RdfProperty(XKOS.temporal)] = None
    before: Annotated[list[str | URIRef | StatisticalConcept] | None, RdfProperty(XKOS.before)] = None
    after: Annotated[list[str | URIRef | StatisticalConcept] | None, RdfProperty(XKOS.after)] = None

    # Part-whole relationships
    is_part_of: Annotated[list[str | URIRef | StatisticalConcept] | None, RdfProperty(XKOS.isPartOf)] = None
    has_part: Annotated[list[str | URIRef | StatisticalConcept] | None, RdfProperty(XKOS.hasPart)] = None

    # Specialization
    specializes: Annotated[list[str | URIRef | StatisticalConcept] | None, RdfProperty(XKOS.specializes)] = None
    generalizes: Annotated[list[str | URIRef | StatisticalConcept] | None, RdfProperty(XKOS.generalizes)] = None

    # Level
    class_at: Annotated[
        list[str | URIRef | ClassificationLevel] | None,
        RdfProperty(XKOS.classifiedUnder),
    ] = None

    # Concept relations
    disjoint: Annotated[list[str | URIRef | StatisticalConcept] | None, RdfProperty(XKOS.disjoint)] = None
    broader_generic: Annotated[list[str | URIRef | StatisticalConcept] | None, RdfProperty(XKOS.broaderGeneric)] = None
    narrower_generic: Annotated[
        list[str | URIRef | StatisticalConcept] | None,
        RdfProperty(XKOS.narrowerGeneric),
    ] = None
    broader_partitive: Annotated[
        list[str | URIRef | StatisticalConcept] | None,
        RdfProperty(XKOS.broaderPartitive),
    ] = None
    narrower_partitive: Annotated[
        list[str | URIRef | StatisticalConcept] | None,
        RdfProperty(XKOS.narrowerPartitive),
    ] = None

    # Notes
    introduction: Annotated[list[str] | None, RdfProperty(XKOS.introduction)] = None
    editorial_note: Annotated[list[str] | None, RdfProperty(XKOS.editorialNote)] = None
    change_note: Annotated[list[str] | None, RdfProperty(XKOS.changeNote)] = None


class StatisticalClassification(XkosResource):
    """A SKOS Concept Scheme representing a statistical classification."""

    rdf_type: ClassVar[str] = str(SKOS.ConceptScheme)

    # Labels
    pref_label: Annotated[list[str] | None, RdfProperty(SKOS.prefLabel)] = None
    alt_label: Annotated[list[str] | None, RdfProperty(SKOS.altLabel)] = None

    # Definition and scope
    definition: Annotated[list[str] | None, RdfProperty(SKOS.definition)] = None
    scope_note: Annotated[list[str] | None, RdfProperty(SKOS.scopeNote)] = None

    # Top concepts
    has_top_concept: Annotated[list[str | URIRef | StatisticalConcept] | None, RdfProperty(SKOS.hasTopConcept)] = None

    # XKOS properties
    number_of_levels: Annotated[list[int] | None, RdfProperty(XKOS.numberOfLevels)] = None
    has_level: Annotated[list[str | URIRef | ClassificationLevel] | None, RdfProperty(XKOS.levels)] = None

    # Variants
    variant: Annotated[list[str | URIRef | StatisticalClassification] | None, RdfProperty(XKOS.variant)] = None
    belongs_to: Annotated[list[str | URIRef] | None, RdfProperty(XKOS.belongsTo)] = None

    # Versioning
    follows: Annotated[list[str | URIRef | StatisticalClassification] | None, RdfProperty(XKOS.follows)] = None
    supersedes: Annotated[
        list[str | URIRef | StatisticalClassification] | None,
        RdfProperty(XKOS.supersedes),
    ] = None
    succeeds: Annotated[
        list[str | URIRef | StatisticalClassification] | None,
        RdfProperty(XKOS.succeeds),
    ] = None

    # Relations
    disjoint: Annotated[
        list[str | URIRef | StatisticalClassification] | None,
        RdfProperty(XKOS.disjoint),
    ] = None

    # Notes
    introduction: Annotated[list[str] | None, RdfProperty(XKOS.introduction)] = None
    editorial_note: Annotated[list[str] | None, RdfProperty(XKOS.editorialNote)] = None
    change_note: Annotated[list[str] | None, RdfProperty(XKOS.changeNote)] = None
