"""Tests for VCard vocabulary models."""

from __future__ import annotations

from rdflib import RDF, Graph

from dartfx.rdf.pydantic.vcard import VCARD, Individual, Organization


def test_individual_basic() -> None:
    """Test basic Individual serialization."""
    individual = Individual(
        fn=["John Doe"],
    )

    graph = individual.to_rdf_graph()
    assert len(list(graph.triples((None, None, None)))) > 0

    # Round-trip test - find subject in graph (first subject with rdf:type)
    subjects = list(graph.subjects(RDF.type, VCARD.Individual))
    assert len(subjects) > 0
    subject = subjects[0]

    reloaded = Individual.from_rdf_graph(graph, subject)  # type: ignore[arg-type]
    assert reloaded.fn == "John Doe"


def test_organization_serialization() -> None:
    """Test Organization serialization."""
    org = Organization(
        fn=["ACME Corporation"],
    )

    graph = org.to_rdf_graph()
    subjects = list(graph.subjects(RDF.type, VCARD.Organization))
    assert len(subjects) > 0
    reloaded = Organization.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]

    assert reloaded.fn == "ACME Corporation"


def test_individual_with_nickname() -> None:
    """Test Individual with nickname."""
    individual = Individual(
        fn=["John Doe"],
        nickname=["JD"],
    )

    graph = individual.to_rdf_graph()
    subjects = list(graph.subjects(RDF.type, VCARD.Individual))
    assert len(subjects) > 0
    reloaded = Individual.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]

    assert reloaded.nickname == "JD"


def test_individual_with_url() -> None:
    """Test Individual with URL."""
    individual = Individual(
        fn=["John Doe"],
        url=["https://example.org/john"],
    )

    graph = individual.to_rdf_graph()
    subjects = list(graph.subjects(RDF.type, VCARD.Individual))
    assert len(subjects) > 0
    reloaded = Individual.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]

    assert reloaded.url == "https://example.org/john"


def test_vcard_round_trip() -> None:
    """Test round-trip serialization with VCard models."""
    individual = Individual(
        fn="Jane Doe",
    )

    turtle = individual.to_rdf("turtle")
    g = Graph()
    g.parse(data=turtle, format="turtle")
    subjects = list(g.subjects(RDF.type, VCARD.Individual))
    assert len(subjects) > 0
    reloaded = Individual.from_rdf(turtle, format="turtle", subject=subjects[0])  # type: ignore[arg-type]

    assert reloaded.model_dump() == individual.model_dump()


def test_individual_with_note() -> None:
    """Test Individual with note."""
    individual = Individual(
        fn=["John Doe"],
        note=["Important contact"],
    )

    graph = individual.to_rdf_graph()
    subjects = list(graph.subjects(RDF.type, VCARD.Individual))
    assert len(subjects) > 0
    reloaded = Individual.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]

    assert reloaded.note == "Important contact"
