"""Edge-case tests for RDF serialization and deserialization."""

from __future__ import annotations

from typing import Annotated, ClassVar

from rdflib import RDF, Namespace, URIRef

from dartfx.rdf.pydantic import RdfBaseModel, RdfProperty

SCHEMA = Namespace("https://schema.org/")
EX = Namespace("https://example.org/edge/")


class EdgeThing(RdfBaseModel):
    """Minimal model for edge-case coverage."""

    rdf_type: ClassVar = SCHEMA.Thing
    rdf_namespace: ClassVar = EX
    rdf_prefixes: ClassVar = {"schema": SCHEMA, "ex": EX}

    id: str
    label: Annotated[str | None, RdfProperty(SCHEMA.name)] = None
    tags: Annotated[list[str] | None, RdfProperty(SCHEMA.keywords)] = None
    related: Annotated[list[URIRef] | None, RdfProperty(SCHEMA.relatedTo)] = None


def test_null_and_empty_values_skipped() -> None:
    """Ensure None and empty lists are omitted from the graph."""
    item = EdgeThing(id="edge-1", label=None, tags=[], related=None)

    graph = item.to_rdf_graph()
    subject = URIRef(str(EX) + item.id)

    assert len(list(graph.triples((subject, None, None)))) == 1
    assert list(graph.objects(subject, SCHEMA.name)) == []
    assert list(graph.objects(subject, SCHEMA.keywords)) == []
    assert list(graph.objects(subject, SCHEMA.relatedTo)) == []


def test_empty_list_round_trip_defaults() -> None:
    """Empty lists should deserialize to defaults when not serialized."""
    item = EdgeThing(id="edge-2", label="Edge", tags=[])

    graph = item.to_rdf_graph()
    subjects = list(graph.subjects(RDF.type, SCHEMA.Thing))
    assert len(subjects) > 0
    reloaded = EdgeThing.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]

    assert reloaded.label == "Edge"
    assert reloaded.tags is None


def test_circular_reference_via_uri() -> None:
    """Circular references via URIRefs serialize without recursion."""
    subject = URIRef(str(EX) + "edge-3")
    item = EdgeThing(id="edge-3", label="Self", related=[subject])

    graph = item.to_rdf_graph()
    related_objects = list(graph.objects(subject, SCHEMA.relatedTo))

    assert len(related_objects) == 1
    assert related_objects[0] == subject

    reloaded = EdgeThing.from_rdf_graph(graph, subject)
    assert reloaded.related is not None
    assert len(reloaded.related) == 1
    assert str(reloaded.related[0]) == str(subject)
