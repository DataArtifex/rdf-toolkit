"""SKOS (Simple Knowledge Organization System) vocabulary using Pydantic RDF models.

This module provides Pydantic-based models for the SKOS vocabulary,
allowing easy serialization to and from RDF formats.

References:
- https://www.w3.org/2004/02/skos/
- https://www.w3.org/TR/skos-reference/

"""

from __future__ import annotations
from typing import Annotated, List, Optional, Union, cast

from rdflib import URIRef, SKOS, Namespace

from dartfx.rdf.pydantic_rdf import RdfBaseModel, RdfProperty


class SkosResource(RdfBaseModel):
    """Base class for SKOS resources."""
    
    rdf_namespace = cast(Namespace, SKOS)
    rdf_prefixes = {"skos": cast(Namespace, SKOS)}


class ConceptScheme(SkosResource):
    """A SKOS Concept Scheme - an aggregation of one or more SKOS concepts."""
    
    rdf_type = SKOS.ConceptScheme
    
    id: str
    
    # Lexical labels
    pref_label: Annotated[Optional[List[str]], RdfProperty(SKOS.prefLabel)] = None
    alt_label: Annotated[Optional[List[str]], RdfProperty(SKOS.altLabel)] = None
    hidden_label: Annotated[Optional[List[str]], RdfProperty(SKOS.hiddenLabel)] = None
    
    # Documentation properties
    notation: Annotated[Optional[List[str]], RdfProperty(SKOS.notation)] = None
    note: Annotated[Optional[List[str]], RdfProperty(SKOS.note)] = None
    change_note: Annotated[Optional[List[str]], RdfProperty(SKOS.changeNote)] = None
    definition: Annotated[Optional[List[str]], RdfProperty(SKOS.definition)] = None
    editorial_note: Annotated[Optional[List[str]], RdfProperty(SKOS.editorialNote)] = None
    example: Annotated[Optional[List[str]], RdfProperty(SKOS.example)] = None
    history_note: Annotated[Optional[List[str]], RdfProperty(SKOS.historyNote)] = None
    scope_note: Annotated[Optional[List[str]], RdfProperty(SKOS.scopeNote)] = None
    
    # Scheme relationships
    has_top_concept: Annotated[Optional[List[Union[str, URIRef, Concept]]], RdfProperty(SKOS.hasTopConcept)] = None


class Concept(SkosResource):
    """A SKOS Concept - a unit of thought."""
    
    rdf_type = SKOS.Concept
    
    id: str
    
    # Lexical labels
    pref_label: Annotated[Optional[List[str]], RdfProperty(SKOS.prefLabel)] = None
    alt_label: Annotated[Optional[List[str]], RdfProperty(SKOS.altLabel)] = None
    hidden_label: Annotated[Optional[List[str]], RdfProperty(SKOS.hiddenLabel)] = None
    
    # Documentation properties
    notation: Annotated[Optional[List[str]], RdfProperty(SKOS.notation)] = None
    note: Annotated[Optional[List[str]], RdfProperty(SKOS.note)] = None
    change_note: Annotated[Optional[List[str]], RdfProperty(SKOS.changeNote)] = None
    definition: Annotated[Optional[List[str]], RdfProperty(SKOS.definition)] = None
    editorial_note: Annotated[Optional[List[str]], RdfProperty(SKOS.editorialNote)] = None
    example: Annotated[Optional[List[str]], RdfProperty(SKOS.example)] = None
    history_note: Annotated[Optional[List[str]], RdfProperty(SKOS.historyNote)] = None
    scope_note: Annotated[Optional[List[str]], RdfProperty(SKOS.scopeNote)] = None
    
    # Scheme membership
    in_scheme: Annotated[Optional[List[Union[str, URIRef, ConceptScheme]]], RdfProperty(SKOS.inScheme)] = None
    top_concept_of: Annotated[Optional[List[Union[str, URIRef, ConceptScheme]]], RdfProperty(SKOS.topConceptOf)] = None
    
    # Semantic relations (hierarchical)
    broader: Annotated[Optional[List[Union[str, URIRef, Concept]]], RdfProperty(SKOS.broader)] = None
    narrower: Annotated[Optional[List[Union[str, URIRef, Concept]]], RdfProperty(SKOS.narrower)] = None
    broader_transitive: Annotated[Optional[List[Union[str, URIRef, Concept]]], RdfProperty(SKOS.broaderTransitive)] = None
    narrower_transitive: Annotated[Optional[List[Union[str, URIRef, Concept]]], RdfProperty(SKOS.narrowerTransitive)] = None
    
    # Semantic relations (associative)
    related: Annotated[Optional[List[Union[str, URIRef, Concept]]], RdfProperty(SKOS.related)] = None
    
    # Mapping properties
    close_match: Annotated[Optional[List[Union[str, URIRef, Concept]]], RdfProperty(SKOS.closeMatch)] = None
    exact_match: Annotated[Optional[List[Union[str, URIRef, Concept]]], RdfProperty(SKOS.exactMatch)] = None
    broad_match: Annotated[Optional[List[Union[str, URIRef, Concept]]], RdfProperty(SKOS.broadMatch)] = None
    narrow_match: Annotated[Optional[List[Union[str, URIRef, Concept]]], RdfProperty(SKOS.narrowMatch)] = None
    related_match: Annotated[Optional[List[Union[str, URIRef, Concept]]], RdfProperty(SKOS.relatedMatch)] = None


class Collection(SkosResource):
    """A SKOS Collection - a meaningful grouping of concepts."""
    
    rdf_type = SKOS.Collection
    
    id: str
    
    # Lexical labels
    pref_label: Annotated[Optional[List[str]], RdfProperty(SKOS.prefLabel)] = None
    alt_label: Annotated[Optional[List[str]], RdfProperty(SKOS.altLabel)] = None
    hidden_label: Annotated[Optional[List[str]], RdfProperty(SKOS.hiddenLabel)] = None
    
    # Documentation properties
    notation: Annotated[Optional[List[str]], RdfProperty(SKOS.notation)] = None
    note: Annotated[Optional[List[str]], RdfProperty(SKOS.note)] = None
    
    # Collection membership
    member: Annotated[Optional[List[Union[str, URIRef, Concept, Collection]]], RdfProperty(SKOS.member)] = None


class OrderedCollection(SkosResource):
    """A SKOS Ordered Collection - an ordered grouping of concepts."""
    
    rdf_type = SKOS.OrderedCollection
    
    id: str
    
    # Lexical labels
    pref_label: Annotated[Optional[List[str]], RdfProperty(SKOS.prefLabel)] = None
    alt_label: Annotated[Optional[List[str]], RdfProperty(SKOS.altLabel)] = None
    hidden_label: Annotated[Optional[List[str]], RdfProperty(SKOS.hiddenLabel)] = None
    
    # Documentation properties
    notation: Annotated[Optional[List[str]], RdfProperty(SKOS.notation)] = None
    note: Annotated[Optional[List[str]], RdfProperty(SKOS.note)] = None
    
    # Ordered collection membership
    member_list: Annotated[Optional[List[Union[str, URIRef, Concept]]], RdfProperty(SKOS.memberList)] = None


__all__ = [
    "SkosResource",
    "ConceptScheme",
    "Concept",
    "Collection",
    "OrderedCollection",
]
