"""Tests for ODRL (Open Digital Rights Language) vocabulary models."""

from __future__ import annotations

from rdflib import ODRL2, RDF, Graph

from dartfx.rdf.pydantic.odrl import Action, Constraint, Duty, Permission, Policy, Prohibition


def test_policy_basic() -> None:
    """Test basic ODRL Policy serialization."""
    policy = Policy(uid=["policy-1"])

    graph = policy.to_rdf_graph()
    assert len(list(graph.triples((None, None, None)))) > 0

    subjects = list(graph.subjects(RDF.type, ODRL2.Policy))
    assert len(subjects) > 0
    reloaded = Policy.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]

    assert reloaded.uid == "policy-1"


def test_permission_with_action() -> None:
    """Test Permission with Action and target."""
    action = Action()
    permission = Permission(
        action=[action],
        target=["https://example.org/resource"],
    )
    policy = Policy(permission=[permission])

    graph = policy.to_rdf_graph()
    subjects = list(graph.subjects(RDF.type, ODRL2.Policy))
    assert len(subjects) > 0
    reloaded = Policy.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]

    assert reloaded.permission is not None
    assert isinstance(reloaded.permission, Permission)


def test_prohibition_with_remedy() -> None:
    """Test Prohibition with remedy Duty."""
    remedy = Duty()
    prohibition = Prohibition(remedy=[remedy])

    graph = prohibition.to_rdf_graph()
    subjects = list(graph.subjects(RDF.type, ODRL2.Prohibition))
    assert len(subjects) > 0
    reloaded = Prohibition.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]

    assert reloaded.remedy is not None
    assert isinstance(reloaded.remedy, Duty)


def test_constraint_basic() -> None:
    """Test basic ODRL Constraint serialization."""
    constraint = Constraint(
        left_operand=["count"],
        operator=["gt"],
        right_operand=["5"],
    )

    graph = constraint.to_rdf_graph()
    subjects = list(graph.subjects(RDF.type, ODRL2.Constraint))
    assert len(subjects) > 0
    reloaded = Constraint.from_rdf_graph(graph, subjects[0])  # type: ignore[arg-type]

    assert reloaded.left_operand == "count"
    assert reloaded.right_operand == "5"


def test_odrl_round_trip() -> None:
    """Test round-trip serialization with ODRL models."""
    duty = Duty(action=[Action()], target=["https://example.org/asset"])
    policy = Policy(
        uid=["policy-rt"],
        obligation=[duty],
    )

    turtle = policy.to_rdf("turtle")
    g = Graph()
    g.parse(data=turtle, format="turtle")
    subjects = list(g.subjects(RDF.type, ODRL2.Policy))
    assert len(subjects) > 0
    reloaded = Policy.from_rdf(turtle, format="turtle", subject=subjects[0])  # type: ignore[arg-type]

    assert reloaded.uid == "policy-rt"
    assert reloaded.obligation is not None
