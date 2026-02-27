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

from ._base import LocalizedStr, RdfBaseModel, RdfProperty

# XKOS namespace
XKOS = Namespace("http://rdf-vocabulary.ddialliance.org/xkos#")


class XkosResource(RdfBaseModel):
    """Base class for XKOS resources."""

    rdf_namespace: ClassVar = XKOS
    rdf_prefixes: ClassVar = {"xkos": XKOS, "skos": SKOS}  # type: ignore[dict-item]


class ClassificationLevel(XkosResource):
    """An XKOS Classification Level - a level in a statistical classification."""

    rdf_type: ClassVar[str | URIRef | None] = str(XKOS.ClassificationLevel)

    # Level properties
    depth: Annotated[int | list[int] | None, RdfProperty(XKOS.depth)] = None
    notations_equal: Annotated[str | list[str] | None, RdfProperty(XKOS.notationsEqual)] = None
    organizes: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(XKOS.organizes)] = None
    covers: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(XKOS.covers)] = None
    covers_exhaustively: Annotated[
        str | URIRef | list[str | URIRef] | None,
        RdfProperty(XKOS.coversExhaustively),
    ] = None
    covers_mutually_exclusively: Annotated[
        str | URIRef | list[str | URIRef] | None,
        RdfProperty(XKOS.coversMutuallyExclusively),
    ] = None
    organized_by: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(XKOS.organizedBy)] = None
    notation_pattern: Annotated[str | list[str] | None, RdfProperty(XKOS.notationPattern)] = None
    max_length: Annotated[int | list[int] | None, RdfProperty(XKOS.maxLength)] = None

    # Labels (from SKOS)
    pref_label: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.prefLabel),
    ] = None
    alt_label: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.altLabel),
    ] = None

    # Notes
    note: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.note),
    ] = None


class ConceptAssociation(XkosResource):
    """An XKOS Concept Association - a relationship between concepts in different classifications."""

    rdf_type: ClassVar[str | URIRef | None] = str(XKOS.ConceptAssociation)

    # Source and target
    source_concept: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(XKOS.sourceConcept)] = None
    target_concept: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(XKOS.targetConcept)] = None


class Correspondence(XkosResource):
    """An XKOS Correspondence - a mapping between two classifications."""

    rdf_type: ClassVar[str | URIRef | None] = str(XKOS.Correspondence)

    # Source and target classifications
    compares: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(XKOS.compares)] = None

    # Labels
    pref_label: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.prefLabel),
    ] = None
    alt_label: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.altLabel),
    ] = None

    # Definition
    definition: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.definition),
    ] = None

    # Associations
    made_of: Annotated[
        str | URIRef | ConceptAssociation | list[str | URIRef | ConceptAssociation] | None, RdfProperty(XKOS.madeOf)
    ] = None


class ExplanatoryNote(XkosResource):
    """An XKOS Explanatory Note - additional documentation for a concept."""

    rdf_type: ClassVar[str | URIRef | None] = str(XKOS.ExplanatoryNote)

    # Descriptive text
    plain_text: Annotated[
        LocalizedStr | None,
        RdfProperty(XKOS.plainText),
    ] = None


# Extended SKOS Concept for statistical classifications
class StatisticalConcept(XkosResource):
    """A SKOS Concept with XKOS extensions for statistical classifications."""

    rdf_type: ClassVar[str | URIRef | None] = str(SKOS.Concept)

    # SKOS properties
    pref_label: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.prefLabel),
    ] = None
    alt_label: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.altLabel),
    ] = None
    hidden_label: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.hiddenLabel),
    ] = None
    notation: Annotated[str | list[str] | None, RdfProperty(SKOS.notation)] = None
    definition: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.definition),
    ] = None

    # SKOS semantic relations
    broader: Annotated[
        str | URIRef | StatisticalConcept | list[str | URIRef | StatisticalConcept] | None, RdfProperty(SKOS.broader)
    ] = None
    narrower: Annotated[
        str | URIRef | StatisticalConcept | list[str | URIRef | StatisticalConcept] | None, RdfProperty(SKOS.narrower)
    ] = None
    related: Annotated[
        str | URIRef | StatisticalConcept | list[str | URIRef | StatisticalConcept] | None, RdfProperty(SKOS.related)
    ] = None

    # Concept scheme
    in_scheme: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(SKOS.inScheme)] = None
    top_concept_of: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(SKOS.topConceptOf)] = None

    # XKOS extensions
    core_content_note: Annotated[
        LocalizedStr | None,
        RdfProperty(XKOS.coreContentNote),
    ] = None
    additional_content_note: Annotated[
        LocalizedStr | None,
        RdfProperty(XKOS.additionalContentNote),
    ] = None
    exclusion_note: Annotated[
        LocalizedStr | None,
        RdfProperty(XKOS.exclusionNote),
    ] = None
    inclusion_note: Annotated[
        LocalizedStr | None,
        RdfProperty(XKOS.inclusionNote),
    ] = None

    # Causal relationships
    causal: Annotated[
        str | URIRef | StatisticalConcept | list[str | URIRef | StatisticalConcept] | None, RdfProperty(XKOS.causal)
    ] = None
    causes: Annotated[
        str | URIRef | StatisticalConcept | list[str | URIRef | StatisticalConcept] | None, RdfProperty(XKOS.causes)
    ] = None
    caused_by: Annotated[
        str | URIRef | StatisticalConcept | list[str | URIRef | StatisticalConcept] | None, RdfProperty(XKOS.causedBy)
    ] = None

    # Sequential relationships
    sequential: Annotated[
        str | URIRef | StatisticalConcept | list[str | URIRef | StatisticalConcept] | None, RdfProperty(XKOS.sequential)
    ] = None
    precedes: Annotated[
        str | URIRef | StatisticalConcept | list[str | URIRef | StatisticalConcept] | None, RdfProperty(XKOS.precedes)
    ] = None
    follows: Annotated[
        str | URIRef | StatisticalConcept | list[str | URIRef | StatisticalConcept] | None, RdfProperty(XKOS.follows)
    ] = None

    # Temporal relationships
    temporal: Annotated[
        str | URIRef | StatisticalConcept | list[str | URIRef | StatisticalConcept] | None, RdfProperty(XKOS.temporal)
    ] = None
    before: Annotated[
        str | URIRef | StatisticalConcept | list[str | URIRef | StatisticalConcept] | None, RdfProperty(XKOS.before)
    ] = None
    after: Annotated[
        str | URIRef | StatisticalConcept | list[str | URIRef | StatisticalConcept] | None, RdfProperty(XKOS.after)
    ] = None

    # Part-whole relationships
    is_part_of: Annotated[
        str | URIRef | StatisticalConcept | list[str | URIRef | StatisticalConcept] | None, RdfProperty(XKOS.isPartOf)
    ] = None
    has_part: Annotated[
        str | URIRef | StatisticalConcept | list[str | URIRef | StatisticalConcept] | None, RdfProperty(XKOS.hasPart)
    ] = None

    # Specialization
    specializes: Annotated[
        str | URIRef | StatisticalConcept | list[str | URIRef | StatisticalConcept] | None,
        RdfProperty(XKOS.specializes),
    ] = None
    generalizes: Annotated[
        str | URIRef | StatisticalConcept | list[str | URIRef | StatisticalConcept] | None,
        RdfProperty(XKOS.generalizes),
    ] = None

    # Level
    class_at: Annotated[
        str | URIRef | ClassificationLevel | list[str | URIRef | ClassificationLevel] | None,
        RdfProperty(XKOS.classifiedUnder),
    ] = None

    # Concept relations
    disjoint: Annotated[
        str | URIRef | StatisticalConcept | list[str | URIRef | StatisticalConcept] | None, RdfProperty(XKOS.disjoint)
    ] = None
    broader_generic: Annotated[
        str | URIRef | StatisticalConcept | list[str | URIRef | StatisticalConcept] | None,
        RdfProperty(XKOS.broaderGeneric),
    ] = None
    narrower_generic: Annotated[
        str | URIRef | StatisticalConcept | list[str | URIRef | StatisticalConcept] | None,
        RdfProperty(XKOS.narrowerGeneric),
    ] = None
    broader_partitive: Annotated[
        str | URIRef | StatisticalConcept | list[str | URIRef | StatisticalConcept] | None,
        RdfProperty(XKOS.broaderPartitive),
    ] = None
    narrower_partitive: Annotated[
        str | URIRef | StatisticalConcept | list[str | URIRef | StatisticalConcept] | None,
        RdfProperty(XKOS.narrowerPartitive),
    ] = None

    # Notes
    introduction: Annotated[
        LocalizedStr | None,
        RdfProperty(XKOS.introduction),
    ] = None
    editorial_note: Annotated[
        LocalizedStr | None,
        RdfProperty(XKOS.editorialNote),
    ] = None
    change_note: Annotated[
        LocalizedStr | None,
        RdfProperty(XKOS.changeNote),
    ] = None


class StatisticalClassification(XkosResource):
    """A SKOS Concept Scheme representing a statistical classification."""

    rdf_type: ClassVar[str | URIRef | None] = str(SKOS.ConceptScheme)

    # Labels
    pref_label: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.prefLabel),
    ] = None
    alt_label: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.altLabel),
    ] = None

    # Definition and scope
    definition: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.definition),
    ] = None
    scope_note: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.scopeNote),
    ] = None

    # Top concepts
    has_top_concept: Annotated[
        str | URIRef | StatisticalConcept | list[str | URIRef | StatisticalConcept] | None,
        RdfProperty(SKOS.hasTopConcept),
    ] = None

    # XKOS properties
    number_of_levels: Annotated[int | list[int] | None, RdfProperty(XKOS.numberOfLevels)] = None
    has_level: Annotated[
        str | URIRef | ClassificationLevel | list[str | URIRef | ClassificationLevel] | None, RdfProperty(XKOS.levels)
    ] = None

    # Variants
    variant: Annotated[
        str | URIRef | StatisticalClassification | list[str | URIRef | StatisticalClassification] | None,
        RdfProperty(XKOS.variant),
    ] = None
    belongs_to: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(XKOS.belongsTo)] = None

    # Versioning
    follows: Annotated[
        str | URIRef | StatisticalClassification | list[str | URIRef | StatisticalClassification] | None,
        RdfProperty(XKOS.follows),
    ] = None
    supersedes: Annotated[
        str | URIRef | StatisticalClassification | list[str | URIRef | StatisticalClassification] | None,
        RdfProperty(XKOS.supersedes),
    ] = None
    succeeds: Annotated[
        str | URIRef | StatisticalClassification | list[str | URIRef | StatisticalClassification] | None,
        RdfProperty(XKOS.succeeds),
    ] = None

    # Relations
    disjoint: Annotated[
        str | URIRef | StatisticalClassification | list[str | URIRef | StatisticalClassification] | None,
        RdfProperty(XKOS.disjoint),
    ] = None

    # Notes
    introduction: Annotated[
        LocalizedStr | None,
        RdfProperty(XKOS.introduction),
    ] = None
    editorial_note: Annotated[
        LocalizedStr | None,
        RdfProperty(XKOS.editorialNote),
    ] = None
    change_note: Annotated[
        LocalizedStr | None,
        RdfProperty(XKOS.changeNote),
    ] = None
