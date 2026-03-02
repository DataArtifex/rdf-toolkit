"""Tests for DCTERMS (Dublin Core Terms) vocabulary models."""

from __future__ import annotations

from datetime import datetime

from rdflib import RDF, Graph

from dartfx.rdf.pydantic import LangString
from dartfx.rdf.pydantic.dcterms import DCTERMS, Agent, DcmiFrequency, DublinCoreRecord


def test_dublin_core_record_basic() -> None:
    """Test basic DublinCoreRecord serialization."""
    record = DublinCoreRecord(
        id="record-1",
        title="Test Record",
        description="A simple description",
    )

    graph = record.to_rdf_graph()
    assert len(list(graph.triples((None, None, None)))) > 0

    subjects = list(graph.subjects(DCTERMS.title, None))
    assert len(subjects) > 0
    reloaded = DublinCoreRecord.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]

    assert reloaded.title == [LangString(value="Test Record", lang=None)]
    assert reloaded.description == [LangString(value="A simple description", lang=None)]


def test_dublin_core_record_with_dates() -> None:
    """Test DublinCoreRecord with date fields."""
    created_at = datetime(2024, 1, 2)
    record = DublinCoreRecord(
        id="record-2",
        title="Temporal Record",
        created=created_at,
        accrual_periodicity=DcmiFrequency.ANNUAL,
    )

    graph = record.to_rdf_graph()
    subjects = list(graph.subjects(DCTERMS.title, None))
    assert len(subjects) > 0
    reloaded = DublinCoreRecord.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]

    assert reloaded.created == created_at
    assert str(reloaded.accrual_periodicity) == DcmiFrequency.ANNUAL


def test_dublin_core_record_with_contributors() -> None:
    """Test DublinCoreRecord with contributor list."""
    record = DublinCoreRecord(
        id="record-3",
        title="Collaborative Record",
        contributor=["Alice", "Bob"],
    )

    graph = record.to_rdf_graph()
    subjects = list(graph.subjects(DCTERMS.title, None))
    assert len(subjects) > 0
    reloaded = DublinCoreRecord.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]

    assert reloaded.contributor == ["Alice", "Bob"]


def test_agent_basic() -> None:
    """Test basic DCTERMS Agent serialization."""
    agent = Agent(
        id="agent-1",
        name="Alice",
        valid=datetime(2024, 2, 1),
    )

    graph = agent.to_rdf_graph()
    subjects = list(graph.subjects(RDF.type, DCTERMS.Agent))
    assert len(subjects) > 0
    reloaded = Agent.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]

    assert reloaded.name == [LangString(value="Alice", lang=None)]


def test_dcterms_round_trip() -> None:
    """Test round-trip serialization with DCTERMS models."""
    record = DublinCoreRecord(
        id="record-rt",
        title="Round Trip",
        subject=["Metadata", "RDF"],
    )

    turtle = record.to_rdf("turtle")
    g = Graph()
    g.parse(data=turtle, format="turtle")
    subjects = list(g.subjects(DCTERMS.title, None))
    assert len(subjects) > 0
    reloaded = DublinCoreRecord.from_rdf(turtle, format="turtle", subject=subjects[0])  # type: ignore[arg-type]

    assert reloaded.model_dump() == record.model_dump()
