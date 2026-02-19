"""Tests for PROV (Provenance Ontology) vocabulary models."""

from __future__ import annotations

from rdflib import RDF, Graph

from dartfx.rdf.pydantic.prov import PROV, Activity, Agent, Entity


def test_entity_basic_serialization() -> None:
    """Test basic Entity serialization."""
    entity = Entity(
        value=["Test Entity"],
    )

    graph = entity.to_rdf_graph()
    assert len(list(graph.triples((None, None, None)))) > 0

    # Round-trip test
    subjects = list(graph.subjects(RDF.type, PROV.Entity))
    assert len(subjects) > 0
    reloaded = Entity.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]
    assert reloaded.value == ["Test Entity"]


def test_activity_basic_serialization() -> None:
    """Test basic Activity serialization."""
    activity = Activity()

    graph = activity.to_rdf_graph()
    assert len(list(graph.triples((None, None, None)))) > 0

    # Round-trip test
    subjects = list(graph.subjects(RDF.type, PROV.Activity))
    assert len(subjects) > 0
    reloaded = Activity.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]
    assert reloaded is not None


def test_agent_serialization() -> None:
    """Test Agent serialization."""
    agent = Agent()

    graph = agent.to_rdf_graph()
    subjects = list(graph.subjects(RDF.type, PROV.Agent))
    assert len(subjects) > 0
    reloaded = Agent.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]

    assert reloaded is not None


def test_entity_derivation() -> None:
    """Test Entity with derivation relationships."""
    source_entity = Entity(value=["Source"])
    derived_entity = Entity(
        value=["Derived"],
        was_derived_from=[source_entity],
    )

    graph = derived_entity.to_rdf_graph()
    subjects = list(graph.subjects(RDF.type, PROV.Entity))
    # Find the derived entity (one with value="Derived")
    subject = None
    for s in subjects:
        values = list(graph.objects(s, PROV.value))
        if values and str(values[0]) == "Derived":
            subject = s
            break

    assert subject is not None
    reloaded = Entity.from_rdf_graph(graph, subject)  # type: ignore[arg-type]

    assert reloaded.value == ["Derived"]
    assert reloaded.was_derived_from is not None
    assert len(reloaded.was_derived_from) == 1


def test_activity_with_entity_usage() -> None:
    """Test Activity using entities."""
    entity = Entity(value=["Input"])
    activity = Activity(used=[entity])

    graph = activity.to_rdf_graph()
    subjects = list(graph.subjects(RDF.type, PROV.Activity))
    assert len(subjects) > 0
    reloaded = Activity.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]

    assert reloaded.used is not None
    assert len(reloaded.used) == 1


def test_prov_round_trip() -> None:
    """Test round-trip serialization with PROV models."""
    entity = Entity(value=["Test"])

    turtle = entity.to_rdf("turtle")
    g = Graph()
    g.parse(data=turtle, format="turtle")
    subjects = list(g.subjects(RDF.type, PROV.Entity))
    assert len(subjects) > 0
    reloaded = Entity.from_rdf(turtle, format="turtle", subject=subjects[0])  # type: ignore[arg-type]

    assert reloaded.model_dump() == entity.model_dump()


def test_entity_with_attribution() -> None:
    """Test Entity attributed to an Agent."""
    agent = Agent()
    entity = Entity(
        value=["Attributed Entity"],
        was_attributed_to=[agent],
    )

    graph = entity.to_rdf_graph()
    subjects = list(graph.subjects(RDF.type, PROV.Entity))
    assert len(subjects) > 0
    reloaded = Entity.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]

    assert reloaded.was_attributed_to is not None
    assert len(reloaded.was_attributed_to) == 1
