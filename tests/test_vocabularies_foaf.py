"""Tests for FOAF (Friend of a Friend) vocabulary models - Revised."""

from __future__ import annotations

from rdflib import RDF

from dartfx.rdf.pydantic.foaf import FOAF, Agent, Document, Organization, Person


def test_document_basic() -> None:
    """Test basic FOAF Document serialization."""
    document = Document(
        topic=["Technology"],
    )

    graph = document.to_rdf_graph()
    assert len(list(graph.triples((None, None, None)))) > 0

    # Round-trip test - extract subject from graph
    subjects = list(graph.subjects(RDF.type, FOAF.Document))
    assert len(subjects) > 0
    reloaded = Document.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]
    assert reloaded.topic == "Technology"


def test_person_basic() -> None:
    """Test basic Person serialization."""
    person = Person(
        name=["John Doe"],
    )

    graph = person.to_rdf_graph()
    assert len(list(graph.triples((None, None, None)))) > 0

    # Round-trip test
    subjects = list(graph.subjects(RDF.type, FOAF.Person))
    assert len(subjects) > 0
    reloaded = Person.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]
    assert reloaded.name == "John Doe"


def test_organization_basic() -> None:
    """Test basic Organization serialization."""
    org = Organization(
        name=["ACME Corp"],
    )

    graph = org.to_rdf_graph()
    assert len(list(graph.triples((None, None, None)))) > 0

    # Round-trip test
    subjects = list(graph.subjects(RDF.type, FOAF.Organization))
    assert len(subjects) > 0
    reloaded = Organization.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]
    assert reloaded.name == "ACME Corp"


def test_agent_basic() -> None:
    """Test basic Agent serialization."""
    agent = Agent()

    graph = agent.to_rdf_graph()
    assert len(list(graph.triples((None, None, None)))) > 0

    # Round-trip test
    subjects = list(graph.subjects(RDF.type, FOAF.Agent))
    assert len(subjects) > 0
    reloaded = Agent.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]
    assert reloaded is not None


def test_foaf_round_trip() -> None:
    """Test round-trip serialization with FOAF models."""
    from rdflib import Graph

    person = Person(name="Jane Doe")

    turtle = person.to_rdf("turtle")
    g = Graph()
    g.parse(data=turtle, format="turtle")
    subjects = list(g.subjects(RDF.type, FOAF.Person))
    assert len(subjects) > 0
    reloaded = Person.from_rdf(turtle, format="turtle", subject=subjects[0])  # type: ignore[arg-type]

    assert reloaded.model_dump() == person.model_dump()
