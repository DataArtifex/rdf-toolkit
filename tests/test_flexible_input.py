"""Tests for flexible input types (scalar vs list) across vocabularies."""

from __future__ import annotations

from rdflib import RDF, URIRef

from dartfx.rdf.pydantic.dcterms import DublinCoreRecord
from dartfx.rdf.pydantic.foaf import Person
from dartfx.rdf.pydantic.odrl import Offer, Permission
from dartfx.rdf.pydantic.prov import Entity
from dartfx.rdf.pydantic.skos import Concept


def test_skos_flexible_input() -> None:
    """Test SKOS models accept scalar strings for labels and documentation."""
    # Test with single strings
    concept = Concept(
        id="http://example.org/c1", pref_label="Main Label", definition="A single string definition", notation="N1"
    )

    graph = concept.to_rdf_graph()

    # Verify triples exist
    from dartfx.rdf.pydantic.skos import SKOS

    assert (URIRef("http://example.org/c1"), SKOS.prefLabel, None) in graph

    # Test Round-trip
    # Note: reloaded items will currently be in list form because RDF is inherently multi-valued
    reloaded = Concept.from_rdf_graph(graph, URIRef("http://example.org/c1"))
    assert reloaded.pref_label == ["Main Label"]
    assert reloaded.definition == ["A single string definition"]
    assert reloaded.notation == ["N1"]


def test_foaf_flexible_input() -> None:
    """Test FOAF models accept scalar values."""
    person = Person(name="John Doe", mbox="mailto:john@example.com", homepage=URIRef("http://example.org/john"))

    graph = person.to_rdf_graph()
    from dartfx.rdf.pydantic.foaf import FOAF

    # Find the person node (it's blank)
    subjects = list(graph.subjects(RDF.type, FOAF.Person))
    assert len(subjects) > 0
    subject = subjects[0]

    assert (subject, FOAF.name, None) in graph
    assert (subject, FOAF.mbox, None) in graph

    reloaded = Person.from_rdf_graph(graph, subject)
    assert reloaded.name == ["John Doe"]
    assert reloaded.mbox == ["mailto:john@example.com"]


def test_dcterms_flexible_input() -> None:
    """Test Dublin Core models accept scalar values."""
    doc = DublinCoreRecord(
        id="http://example.org/doc1", title="My Document", creator="Author Name", description="A single description"
    )

    graph = doc.to_rdf_graph()
    from dartfx.rdf.pydantic.dcterms import DCTERMS

    subject = URIRef("http://example.org/doc1")
    assert (subject, DCTERMS.title, None) in graph

    reloaded = DublinCoreRecord.from_rdf_graph(graph, subject)
    assert reloaded.title == ["My Document"]
    assert reloaded.creator == ["Author Name"]


def test_prov_flexible_input() -> None:
    """Test PROV models accept scalar values."""
    entity = Entity(was_attributed_to="http://example.org/agent1")

    graph = entity.to_rdf_graph()
    from dartfx.rdf.pydantic.prov import PROV

    # Verify triples exist in the graph
    assert (None, RDF.type, PROV.Entity) in graph
    assert (None, PROV.wasAttributedTo, URIRef("http://example.org/agent1")) in graph


def test_odrl_flexible_input() -> None:
    """Test ODRL models accept scalar values."""
    offer = Offer(permission=Permission(action="http://www.w3.org/ns/odrl/2/play", target="http://example.com/music/1"))

    graph = offer.to_rdf_graph()
    from dartfx.rdf.pydantic.odrl import ODRL2

    # Verify triples exist in the graph (this is the true test of serialization)
    assert (None, RDF.type, ODRL2.Offer) in graph

    # Find the permission node
    permissions = list(graph.objects(None, ODRL2.permission))
    assert len(permissions) == 1
    p_node = permissions[0]

    # Verify action was serialized as a URIRef (due to my URIRef union fix)
    assert (p_node, ODRL2.action, URIRef("http://www.w3.org/ns/odrl/2/play")) in graph
    assert (p_node, ODRL2.target, URIRef("http://example.com/music/1")) in graph

    # For now, we don't test round-trip of action=URIRef because without 'id' fields
    # defined in models, reloaded objects lose their URI identity.


def test_mixed_input() -> None:
    """Test mixing scalar and list inputs."""
    concept = Concept(id="http://example.org/mixed", pref_label="Single", alt_label=["List 1", "List 2"])

    graph = concept.to_rdf_graph()
    from dartfx.rdf.pydantic.skos import SKOS

    assert (URIRef("http://example.org/mixed"), SKOS.prefLabel, None) in graph
    assert len(list(graph.objects(URIRef("http://example.org/mixed"), SKOS.altLabel))) == 2

    reloaded = Concept.from_rdf_graph(graph, URIRef("http://example.org/mixed"))
    assert reloaded.pref_label == ["Single"]
    assert len(reloaded.alt_label) == 2
