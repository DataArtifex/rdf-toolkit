"""SKOS (Simple Knowledge Organization System) vocabulary using Pydantic RDF models.

This module provides Pydantic-based models for the SKOS vocabulary,
allowing easy serialization to and from RDF formats.

References:
- https://www.w3.org/2004/02/skos/
- https://www.w3.org/TR/skos-reference/

"""

from __future__ import annotations

from typing import Annotated, cast

from rdflib import SKOS, Namespace, URIRef

from ._base import LocalizedStr, RdfBaseModel, RdfProperty


class SkosResource(RdfBaseModel):
    """Base class for SKOS resources."""

    rdf_namespace = cast(Namespace, SKOS)
    rdf_prefixes = {"skos": cast(Namespace, SKOS)}


SKOSXL = Namespace("http://www.w3.org/2008/05/skos-xl#")


class Label(SkosResource):
    """A SKOS-XL Label."""

    rdf_type = SKOSXL.Label
    rdf_namespace = SKOSXL
    rdf_prefixes = {"skosxl": SKOSXL}

    literal_form: Annotated[str, RdfProperty(SKOSXL.literalForm)]


class ConceptScheme(SkosResource):
    """A SKOS Concept Scheme - an aggregation of one or more SKOS concepts."""

    rdf_type = SKOS.ConceptScheme

    id: str

    # Lexical labels
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

    # SKOS-XL labels
    pref_label_xl: Annotated[
        str | URIRef | Label | list[str | URIRef | Label] | None, RdfProperty(SKOSXL.prefLabel)
    ] = None
    alt_label_xl: Annotated[str | URIRef | Label | list[str | URIRef | Label] | None, RdfProperty(SKOSXL.altLabel)] = (
        None
    )
    hidden_label_xl: Annotated[
        str | URIRef | Label | list[str | URIRef | Label] | None, RdfProperty(SKOSXL.hiddenLabel)
    ] = None

    # Documentation properties
    notation: Annotated[str | list[str] | None, RdfProperty(SKOS.notation)] = None
    note: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.note),
    ] = None
    change_note: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.changeNote),
    ] = None
    definition: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.definition),
    ] = None
    editorial_note: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.editorialNote),
    ] = None
    example: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.example),
    ] = None
    history_note: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.historyNote),
    ] = None
    scope_note: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.scopeNote),
    ] = None

    # Scheme relationships
    has_top_concept: Annotated[
        str | URIRef | Concept | list[str | URIRef | Concept] | None, RdfProperty(SKOS.hasTopConcept)
    ] = None


class Concept(SkosResource):
    """A SKOS Concept - a unit of thought."""

    rdf_type = SKOS.Concept

    id: str

    # Lexical labels
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

    # SKOS-XL labels
    pref_label_xl: Annotated[
        str | URIRef | Label | list[str | URIRef | Label] | None, RdfProperty(SKOSXL.prefLabel)
    ] = None
    alt_label_xl: Annotated[str | URIRef | Label | list[str | URIRef | Label] | None, RdfProperty(SKOSXL.altLabel)] = (
        None
    )
    hidden_label_xl: Annotated[
        str | URIRef | Label | list[str | URIRef | Label] | None, RdfProperty(SKOSXL.hiddenLabel)
    ] = None

    # Documentation properties
    notation: Annotated[str | list[str] | None, RdfProperty(SKOS.notation)] = None
    note: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.note),
    ] = None
    change_note: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.changeNote),
    ] = None
    definition: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.definition),
    ] = None
    editorial_note: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.editorialNote),
    ] = None
    example: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.example),
    ] = None
    history_note: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.historyNote),
    ] = None
    scope_note: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.scopeNote),
    ] = None

    # Scheme membership
    in_scheme: Annotated[
        str | URIRef | ConceptScheme | list[str | URIRef | ConceptScheme] | None, RdfProperty(SKOS.inScheme)
    ] = None
    top_concept_of: Annotated[
        str | URIRef | ConceptScheme | list[str | URIRef | ConceptScheme] | None, RdfProperty(SKOS.topConceptOf)
    ] = None

    # Semantic relations (hierarchical)
    broader: Annotated[str | URIRef | Concept | list[str | URIRef | Concept] | None, RdfProperty(SKOS.broader)] = None
    narrower: Annotated[str | URIRef | Concept | list[str | URIRef | Concept] | None, RdfProperty(SKOS.narrower)] = None
    broader_transitive: Annotated[
        str | URIRef | Concept | list[str | URIRef | Concept] | None, RdfProperty(SKOS.broaderTransitive)
    ] = None
    narrower_transitive: Annotated[
        str | URIRef | Concept | list[str | URIRef | Concept] | None, RdfProperty(SKOS.narrowerTransitive)
    ] = None

    # Semantic relations (associative)
    related: Annotated[str | URIRef | Concept | list[str | URIRef | Concept] | None, RdfProperty(SKOS.related)] = None

    # Mapping properties
    close_match: Annotated[
        str | URIRef | Concept | list[str | URIRef | Concept] | None, RdfProperty(SKOS.closeMatch)
    ] = None
    exact_match: Annotated[
        str | URIRef | Concept | list[str | URIRef | Concept] | None, RdfProperty(SKOS.exactMatch)
    ] = None
    broad_match: Annotated[
        str | URIRef | Concept | list[str | URIRef | Concept] | None, RdfProperty(SKOS.broadMatch)
    ] = None
    narrow_match: Annotated[
        str | URIRef | Concept | list[str | URIRef | Concept] | None, RdfProperty(SKOS.narrowMatch)
    ] = None
    related_match: Annotated[
        str | URIRef | Concept | list[str | URIRef | Concept] | None, RdfProperty(SKOS.relatedMatch)
    ] = None

    # Super-properties
    semantic_relation: Annotated[
        str | URIRef | Concept | list[str | URIRef | Concept] | None, RdfProperty(SKOS.semanticRelation)
    ] = None
    mapping_relation: Annotated[
        str | URIRef | Concept | list[str | URIRef | Concept] | None, RdfProperty(SKOS.mappingRelation)
    ] = None


class Collection(SkosResource):
    """A SKOS Collection - a meaningful grouping of concepts."""

    rdf_type = SKOS.Collection

    id: str

    # Lexical labels
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

    # Documentation properties
    notation: Annotated[str | list[str] | None, RdfProperty(SKOS.notation)] = None
    note: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.note),
    ] = None

    # Collection membership
    member: Annotated[
        str | URIRef | Concept | Collection | list[str | URIRef | Concept | Collection] | None,
        RdfProperty(SKOS.member),
    ] = None


class OrderedCollection(SkosResource):
    """A SKOS Ordered Collection - an ordered grouping of concepts."""

    rdf_type = SKOS.OrderedCollection

    id: str

    # Lexical labels
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

    # Documentation properties
    notation: Annotated[str | list[str] | None, RdfProperty(SKOS.notation)] = None
    note: Annotated[
        LocalizedStr | None,
        RdfProperty(SKOS.note),
    ] = None

    # Ordered collection membership
    member_list: Annotated[
        str | URIRef | Concept | list[str | URIRef | Concept] | None, RdfProperty(SKOS.memberList)
    ] = None


__all__ = [
    "SkosResource",
    "ConceptScheme",
    "Concept",
    "Collection",
    "OrderedCollection",
    "Label",
]
