"""Tests for XKOS (Extended Knowledge Organization System) vocabulary models."""

from __future__ import annotations

from rdflib import RDF, SKOS, Graph

from dartfx.rdf.pydantic import LangString
from dartfx.rdf.pydantic.xkos import (
    XKOS,
    ClassificationLevel,
    ConceptAssociation,
    Correspondence,
    StatisticalClassification,
    StatisticalConcept,
)


def test_classification_level_basic() -> None:
    """Test basic ClassificationLevel serialization."""
    level = ClassificationLevel(
        depth=[1],
        pref_label=["Level 1"],
    )

    graph = level.to_rdf_graph()
    assert len(list(graph.triples((None, None, None)))) > 0

    subjects = list(graph.subjects(RDF.type, XKOS.ClassificationLevel))
    assert len(subjects) > 0
    reloaded = ClassificationLevel.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]

    assert reloaded.depth == 1
    assert reloaded.pref_label == [LangString(value="Level 1", lang=None)]


def test_statistical_concept_basic() -> None:
    """Test basic StatisticalConcept serialization."""
    concept = StatisticalConcept(
        pref_label=["Age"],
        notation=["A"],
    )

    graph = concept.to_rdf_graph()
    subjects = list(graph.subjects(RDF.type, SKOS.Concept))
    assert len(subjects) > 0
    reloaded = StatisticalConcept.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]

    assert reloaded.pref_label == [LangString(value="Age", lang=None)]


def test_statistical_classification_with_top_concept() -> None:
    """Test StatisticalClassification with top concept."""
    concept = StatisticalConcept(pref_label=["Population"])
    classification = StatisticalClassification(
        pref_label=["Demo Classification"],
        has_top_concept=[concept],
        number_of_levels=[1],
    )

    graph = classification.to_rdf_graph()
    subjects = list(graph.subjects(RDF.type, SKOS.ConceptScheme))
    assert len(subjects) > 0
    reloaded = StatisticalClassification.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]

    assert reloaded.has_top_concept is not None
    assert isinstance(reloaded.has_top_concept, StatisticalConcept)


def test_correspondence_with_association() -> None:
    """Test Correspondence with ConceptAssociation."""
    association = ConceptAssociation(
        source_concept=["concept-a"],
        target_concept=["concept-b"],
    )
    correspondence = Correspondence(
        pref_label=["Mapping"],
        made_of=[association],
    )

    graph = correspondence.to_rdf_graph()
    subjects = list(graph.subjects(RDF.type, XKOS.Correspondence))
    assert len(subjects) > 0
    reloaded = Correspondence.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]

    assert reloaded.made_of is not None
    assert isinstance(reloaded.made_of, ConceptAssociation)


def test_xkos_round_trip() -> None:
    """Test round-trip serialization with XKOS models."""
    concept = StatisticalConcept(
        pref_label="Round Trip",
    )

    turtle = concept.to_rdf("turtle")
    g = Graph()
    g.parse(data=turtle, format="turtle")
    subjects = list(g.subjects(RDF.type, SKOS.Concept))
    assert len(subjects) > 0
    reloaded = StatisticalConcept.from_rdf(turtle, format="turtle", subject=subjects[0])  # type: ignore[arg-type]

    assert reloaded.model_dump() == concept.model_dump()
