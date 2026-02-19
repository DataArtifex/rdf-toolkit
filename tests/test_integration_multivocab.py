"""Integration tests for multi-vocabulary graphs."""

from __future__ import annotations

from rdflib import ODRL2, RDF, SKOS, Graph

from dartfx.rdf.pydantic.dcterms import DCTERMS, DublinCoreRecord
from dartfx.rdf.pydantic.foaf import FOAF, Person
from dartfx.rdf.pydantic.odrl import Policy
from dartfx.rdf.pydantic.xkos import StatisticalClassification, StatisticalConcept


def test_multivocab_graph_round_trip() -> None:
    """Round-trip multiple vocabularies in a shared graph."""
    graph = Graph()

    person = Person(name=["Alice"])
    record = DublinCoreRecord(id="record-1", title="Integrated Record", creator="Alice")
    policy = Policy(uid=["policy-1"])

    person.to_rdf_graph(graph)
    record.to_rdf_graph(graph)
    policy.to_rdf_graph(graph)

    person_subjects = list(graph.subjects(RDF.type, FOAF.Person))
    record_subjects = list(graph.subjects(DCTERMS.title, None))
    policy_subjects = list(graph.subjects(RDF.type, ODRL2.Policy))

    assert person_subjects
    assert record_subjects
    assert policy_subjects

    reloaded_person = Person.from_rdf_graph(graph, person_subjects[0])  # type: ignore[arg-type]
    reloaded_record = DublinCoreRecord.from_rdf_graph(graph, record_subjects[0])  # type: ignore[arg-type]
    reloaded_policy = Policy.from_rdf_graph(graph, policy_subjects[0])  # type: ignore[arg-type]

    assert reloaded_person.name == ["Alice"]
    assert reloaded_record.title == "Integrated Record"
    assert reloaded_policy.uid == ["policy-1"]


def test_skos_xkos_shared_graph() -> None:
    """Ensure SKOS and XKOS resources coexist in one graph."""
    graph = Graph()

    concept = StatisticalConcept(pref_label=["Population"])
    classification = StatisticalClassification(
        pref_label=["Demo Classification"],
        has_top_concept=[concept],
        number_of_levels=[1],
    )

    concept.to_rdf_graph(graph)
    classification.to_rdf_graph(graph)

    concept_subjects = list(graph.subjects(RDF.type, SKOS.Concept))
    scheme_subjects = list(graph.subjects(RDF.type, SKOS.ConceptScheme))

    assert concept_subjects
    assert scheme_subjects

    reloaded_concept = StatisticalConcept.from_rdf_graph(graph, concept_subjects[0])  # type: ignore[arg-type]
    reloaded_scheme = StatisticalClassification.from_rdf_graph(graph, scheme_subjects[0])  # type: ignore[arg-type]

    assert reloaded_concept.pref_label == ["Population"]
    assert reloaded_scheme.pref_label == ["Demo Classification"]
