"""Tests for SKOS (Simple Knowledge Organization System) vocabulary models."""

from __future__ import annotations

from rdflib import RDF, Graph

from dartfx.rdf.pydantic.skos import SKOS, Collection, Concept, ConceptScheme


def test_concept_scheme_basic() -> None:
    """Test basic ConceptScheme serialization."""
    scheme = ConceptScheme(
        id="scheme-1",
        pref_label=["Test Scheme"],
    )

    graph = scheme.to_rdf_graph()
    assert len(list(graph.triples((None, None, None)))) > 0

    # Round-trip test
    subjects = list(graph.subjects(RDF.type, SKOS.ConceptScheme))
    assert len(subjects) > 0
    reloaded = ConceptScheme.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]
    assert reloaded.pref_label == "Test Scheme"


def test_concept_basic() -> None:
    """Test basic Concept serialization."""
    concept = Concept(
        id="concept-1",
        pref_label=["Concept Label"],
        definition=["A test concept"],
    )

    graph = concept.to_rdf_graph()
    subjects = list(graph.subjects(RDF.type, SKOS.Concept))
    assert len(subjects) > 0
    reloaded = Concept.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]

    assert reloaded.pref_label == "Concept Label"
    assert reloaded.definition == "A test concept"


def test_concept_with_alt_labels() -> None:
    """Test Concept with alternative labels."""
    concept = Concept(
        id="concept-2",
        pref_label=["Primary Label"],
        alt_label=["Alternative 1", "Alternative 2"],
    )

    graph = concept.to_rdf_graph()
    subjects = list(graph.subjects(RDF.type, SKOS.Concept))
    assert len(subjects) > 0
    reloaded = Concept.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]

    assert reloaded.pref_label == "Primary Label"
    assert reloaded.alt_label == ["Alternative 1", "Alternative 2"]


def test_collection_serialization() -> None:
    """Test Collection serialization."""
    collection = Collection(id="collection-1")

    graph = collection.to_rdf_graph()
    subjects = list(graph.subjects(RDF.type, SKOS.Collection))
    assert len(subjects) > 0
    reloaded = Collection.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]

    assert reloaded is not None


def test_skos_round_trip() -> None:
    """Test round-trip serialization with SKOS models."""
    concept = Concept(
        id="test",
        pref_label="Test",
        definition="A test definition",
    )

    turtle = concept.to_rdf("turtle")
    g = Graph()
    g.parse(data=turtle, format="turtle")
    subjects = list(g.subjects(RDF.type, SKOS.Concept))
    assert len(subjects) > 0
    reloaded = Concept.from_rdf(turtle, format="turtle", subject=subjects[0])  # type: ignore[arg-type]

    assert reloaded.model_dump() == concept.model_dump()


def test_concept_with_scope_note() -> None:
    """Test Concept with scope note."""
    concept = Concept(
        id="concept-3",
        pref_label=["Complex Concept"],
        scope_note=["This concept refers to..."],
    )

    graph = concept.to_rdf_graph()
    subjects = list(graph.subjects(RDF.type, SKOS.Concept))
    assert len(subjects) > 0
    reloaded = Concept.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]

    assert reloaded.pref_label == "Complex Concept"
    assert reloaded.scope_note == "This concept refers to..."
