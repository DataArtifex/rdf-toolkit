"""Performance benchmarks for RDF serialization and deserialization."""

from __future__ import annotations

from rdflib import ODRL2, RDF, Graph

from dartfx.rdf.pydantic.dcterms import DCTERMS, DublinCoreRecord
from dartfx.rdf.pydantic.foaf import FOAF, Person
from dartfx.rdf.pydantic.odrl import Action, Duty, Permission, Policy


def test_benchmark_foaf_to_rdf_graph(benchmark) -> None:
    """Benchmark FOAF graph serialization."""
    person = Person(name=["Benchmark User"])

    def run() -> int:
        graph = person.to_rdf_graph()
        return len(list(graph.triples((None, None, None))))

    triple_count = benchmark(run)
    assert triple_count > 0


def test_benchmark_dcterms_round_trip(benchmark) -> None:
    """Benchmark DCTERMS round-trip serialization."""
    record = DublinCoreRecord(
        id="record-bench",
        title="Benchmark Record",
        subject=["RDF", "Benchmark"],
    )

    def run() -> DublinCoreRecord:
        turtle = record.to_rdf("turtle")
        graph = Graph()
        graph.parse(data=turtle, format="turtle")
        subjects = list(graph.subjects(DCTERMS.title, None))
        return DublinCoreRecord.from_rdf(turtle, format="turtle", subject=subjects[0])  # type: ignore[arg-type]

    reloaded = benchmark(run)
    assert reloaded.title == "Benchmark Record"


def test_benchmark_odrl_policy_round_trip(benchmark) -> None:
    """Benchmark ODRL policy round-trip serialization."""
    policy = Policy(
        uid=["policy-bench"],
        permission=[Permission(action=[Action()], target=["https://example.org/asset"])],
        obligation=[Duty(action=[Action()])],
    )

    def run() -> Policy:
        turtle = policy.to_rdf("turtle")
        graph = Graph()
        graph.parse(data=turtle, format="turtle")
        subjects = list(graph.subjects(RDF.type, ODRL2.Policy))
        return Policy.from_rdf(turtle, format="turtle", subject=subjects[0])  # type: ignore[arg-type]

    reloaded = benchmark(run)
    assert reloaded.uid == "policy-bench"


def test_benchmark_foaf_from_rdf_graph(benchmark) -> None:
    """Benchmark FOAF graph deserialization."""
    person = Person(name=["Benchmark Deserialize"])
    graph = person.to_rdf_graph()
    subjects = list(graph.subjects(RDF.type, FOAF.Person))

    def run() -> Person:
        return Person.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]

    reloaded = benchmark(run)
    assert reloaded.name == "Benchmark Deserialize"
