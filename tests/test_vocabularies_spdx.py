"""Tests for SPDX vocabulary models."""

from __future__ import annotations

from rdflib import RDF, Graph

from dartfx.rdf.pydantic.spdx import SPDX, Package, SpdxDocument


def test_package_basic() -> None:
    """Test basic Package serialization."""
    package = Package(
        name=["Test Package"],
        download_location=["https://example.org/test"],
    )

    graph = package.to_rdf_graph()
    assert len(list(graph.triples((None, None, None)))) > 0

    # Round-trip test
    subjects = list(graph.subjects(RDF.type, SPDX.Package))
    assert len(subjects) > 0
    reloaded = Package.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]
    assert reloaded.name == "Test Package"


def test_spdx_document_basic() -> None:
    """Test basic SpdxDocument serialization."""
    doc = SpdxDocument()

    graph = doc.to_rdf_graph()
    assert len(list(graph.triples((None, None, None)))) > 0

    # Round-trip test
    subjects = list(graph.subjects(RDF.type, SPDX.SpdxDocument))
    assert len(subjects) > 0
    reloaded = SpdxDocument.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]
    assert reloaded is not None


def test_package_with_properties() -> None:
    """Test Package with extended properties."""
    package = Package(
        name=["Complex Package"],
        download_location=["https://example.org/complex"],
    )

    graph = package.to_rdf_graph()
    subjects = list(graph.subjects(RDF.type, SPDX.Package))
    assert len(subjects) > 0
    reloaded = Package.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]

    assert reloaded.name == "Complex Package"


def test_spdx_round_trip() -> None:
    """Test round-trip serialization with SPDX models."""
    package = Package(
        name="Test",
        download_location="https://example.org/test",
    )

    turtle = package.to_rdf("turtle")
    g = Graph()
    g.parse(data=turtle, format="turtle")
    subjects = list(g.subjects(RDF.type, SPDX.Package))
    assert len(subjects) > 0
    reloaded = Package.from_rdf(turtle, format="turtle", subject=subjects[0])  # type: ignore[arg-type]

    assert reloaded.model_dump() == package.model_dump()
