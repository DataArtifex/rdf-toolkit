"""XKOS (Extended Knowledge Organization System) vocabulary using Pydantic RDF models.

This module provides Pydantic-based models for the XKOS vocabulary,
which extends SKOS for statistical classifications.

References:
- http://rdf-vocabulary.ddialliance.org/xkos.html
- https://rdf-vocabulary.ddialliance.org/xkos

"""

from __future__ import annotations
from typing import Annotated, List, Optional

from rdflib import Namespace, URIRef, SKOS

from dartfx.rdf.pydantic_rdf import RdfBaseModel, RdfProperty


# XKOS namespace
XKOS = Namespace("http://rdf-vocabulary.ddialliance.org/xkos#")


class XkosResource(RdfBaseModel):
    """Base class for XKOS resources."""
    
    rdf_namespace = XKOS
    rdf_prefixes = {"xkos": XKOS, "skos": SKOS}


class ClassificationLevel(XkosResource):
    """An XKOS Classification Level - a level in a statistical classification."""
    
    rdf_type: str = str(XKOS.ClassificationLevel)
    
    # Level properties
    depth: Annotated[Optional[List[int]], RdfProperty(XKOS.depth)] = None
    notations_equal: Annotated[Optional[List[str]], RdfProperty(XKOS.notationsEqual)] = None
    organizes: Annotated[Optional[List[str | URIRef]], RdfProperty(XKOS.organizes)] = None
    covers: Annotated[Optional[List[str | URIRef]], RdfProperty(XKOS.covers)] = None
    covers_exhaustively: Annotated[Optional[List[str | URIRef]], RdfProperty(XKOS.coversExhaustively)] = None
    covers_mutually_exclusively: Annotated[Optional[List[str | URIRef]], RdfProperty(XKOS.coversMutuallyExclusively)] = None
    
    # Labels (from SKOS)
    pref_label: Annotated[Optional[List[str]], RdfProperty(SKOS.prefLabel)] = None
    alt_label: Annotated[Optional[List[str]], RdfProperty(SKOS.altLabel)] = None
    
    # Notes
    note: Annotated[Optional[List[str]], RdfProperty(SKOS.note)] = None


class ConceptAssociation(XkosResource):
    """An XKOS Concept Association - a relationship between concepts in different classifications."""
    
    rdf_type: str = str(XKOS.ConceptAssociation)
    
    # Source and target
    source_concept: Annotated[Optional[List[str | URIRef]], RdfProperty(XKOS.sourceConcept)] = None
    target_concept: Annotated[Optional[List[str | URIRef]], RdfProperty(XKOS.targetConcept)] = None


class Correspondence(XkosResource):
    """An XKOS Correspondence - a mapping between two classifications."""
    
    rdf_type: str = str(XKOS.Correspondence)
    
    # Source and target classifications
    compares: Annotated[Optional[List[str | URIRef]], RdfProperty(XKOS.compares)] = None
    
    # Labels
    pref_label: Annotated[Optional[List[str]], RdfProperty(SKOS.prefLabel)] = None
    alt_label: Annotated[Optional[List[str]], RdfProperty(SKOS.altLabel)] = None
    
    # Definition
    definition: Annotated[Optional[List[str]], RdfProperty(SKOS.definition)] = None
    
    # Associations
    made_of: Annotated[Optional[List[str | URIRef | ConceptAssociation]], RdfProperty(XKOS.madeOf)] = None


class ExplanatoryNote(XkosResource):
    """An XKOS Explanatory Note - additional documentation for a concept."""
    
    rdf_type: str = str(XKOS.ExplanatoryNote)
    
    # Descriptive text
    plain_text: Annotated[Optional[List[str]], RdfProperty(XKOS.plainText)] = None


# Extended SKOS Concept for statistical classifications
class StatisticalConcept(XkosResource):
    """A SKOS Concept with XKOS extensions for statistical classifications."""
    
    rdf_type: str = str(SKOS.Concept)
    
    # SKOS properties
    pref_label: Annotated[Optional[List[str]], RdfProperty(SKOS.prefLabel)] = None
    alt_label: Annotated[Optional[List[str]], RdfProperty(SKOS.altLabel)] = None
    hidden_label: Annotated[Optional[List[str]], RdfProperty(SKOS.hiddenLabel)] = None
    notation: Annotated[Optional[List[str]], RdfProperty(SKOS.notation)] = None
    definition: Annotated[Optional[List[str]], RdfProperty(SKOS.definition)] = None
    
    # SKOS semantic relations
    broader: Annotated[Optional[List[str | URIRef | StatisticalConcept]], RdfProperty(SKOS.broader)] = None
    narrower: Annotated[Optional[List[str | URIRef | StatisticalConcept]], RdfProperty(SKOS.narrower)] = None
    related: Annotated[Optional[List[str | URIRef | StatisticalConcept]], RdfProperty(SKOS.related)] = None
    
    # Concept scheme
    in_scheme: Annotated[Optional[List[str | URIRef]], RdfProperty(SKOS.inScheme)] = None
    top_concept_of: Annotated[Optional[List[str | URIRef]], RdfProperty(SKOS.topConceptOf)] = None
    
    # XKOS extensions
    core_content_note: Annotated[Optional[List[str]], RdfProperty(XKOS.coreContentNote)] = None
    additional_content_note: Annotated[Optional[List[str]], RdfProperty(XKOS.additionalContentNote)] = None
    exclusion_note: Annotated[Optional[List[str]], RdfProperty(XKOS.exclusionNote)] = None
    inclusion_note: Annotated[Optional[List[str]], RdfProperty(XKOS.inclusionNote)] = None
    
    # Causal relationships
    causal: Annotated[Optional[List[str | URIRef | StatisticalConcept]], RdfProperty(XKOS.causal)] = None
    causes: Annotated[Optional[List[str | URIRef | StatisticalConcept]], RdfProperty(XKOS.causes)] = None
    caused_by: Annotated[Optional[List[str | URIRef | StatisticalConcept]], RdfProperty(XKOS.causedBy)] = None
    
    # Sequential relationships
    sequential: Annotated[Optional[List[str | URIRef | StatisticalConcept]], RdfProperty(XKOS.sequential)] = None
    precedes: Annotated[Optional[List[str | URIRef | StatisticalConcept]], RdfProperty(XKOS.precedes)] = None
    follows: Annotated[Optional[List[str | URIRef | StatisticalConcept]], RdfProperty(XKOS.follows)] = None
    
    # Temporal relationships
    temporal: Annotated[Optional[List[str | URIRef | StatisticalConcept]], RdfProperty(XKOS.temporal)] = None
    before: Annotated[Optional[List[str | URIRef | StatisticalConcept]], RdfProperty(XKOS.before)] = None
    after: Annotated[Optional[List[str | URIRef | StatisticalConcept]], RdfProperty(XKOS.after)] = None
    
    # Part-whole relationships
    is_part_of: Annotated[Optional[List[str | URIRef | StatisticalConcept]], RdfProperty(XKOS.isPartOf)] = None
    has_part: Annotated[Optional[List[str | URIRef | StatisticalConcept]], RdfProperty(XKOS.hasPart)] = None
    
    # Specialization
    specializes: Annotated[Optional[List[str | URIRef | StatisticalConcept]], RdfProperty(XKOS.specializes)] = None
    generalizes: Annotated[Optional[List[str | URIRef | StatisticalConcept]], RdfProperty(XKOS.generalizes)] = None
    
    # Level
    class_at: Annotated[Optional[List[str | URIRef | ClassificationLevel]], RdfProperty(XKOS.classifiedUnder)] = None


class StatisticalClassification(XkosResource):
    """A SKOS Concept Scheme representing a statistical classification."""
    
    rdf_type: str = str(SKOS.ConceptScheme)
    
    # Labels
    pref_label: Annotated[Optional[List[str]], RdfProperty(SKOS.prefLabel)] = None
    alt_label: Annotated[Optional[List[str]], RdfProperty(SKOS.altLabel)] = None
    
    # Definition and scope
    definition: Annotated[Optional[List[str]], RdfProperty(SKOS.definition)] = None
    scope_note: Annotated[Optional[List[str]], RdfProperty(SKOS.scopeNote)] = None
    
    # Top concepts
    has_top_concept: Annotated[Optional[List[str | URIRef | StatisticalConcept]], RdfProperty(SKOS.hasTopConcept)] = None
    
    # XKOS properties
    number_of_levels: Annotated[Optional[List[int]], RdfProperty(XKOS.numberOfLevels)] = None
    has_level: Annotated[Optional[List[str | URIRef | ClassificationLevel]], RdfProperty(XKOS.levels)] = None
    
    # Variants
    variant: Annotated[Optional[List[str | URIRef | StatisticalClassification]], RdfProperty(XKOS.variant)] = None
    belongs_to: Annotated[Optional[List[str | URIRef]], RdfProperty(XKOS.belongsTo)] = None
    
    # Versioning
    follows: Annotated[Optional[List[str | URIRef | StatisticalClassification]], RdfProperty(XKOS.follows)] = None
    supersedes: Annotated[Optional[List[str | URIRef | StatisticalClassification]], RdfProperty(XKOS.supersedes)] = None
