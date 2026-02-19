"""ODRL (Open Digital Rights Language) vocabulary using Pydantic RDF models.

This module provides Pydantic-based models for the ODRL vocabulary,
allowing easy serialization to and from RDF formats.

References:
- https://www.w3.org/TR/odrl-model/
- https://www.w3.org/TR/odrl-vocab/

"""

from __future__ import annotations

from typing import Annotated, ClassVar

from rdflib import ODRL2, URIRef

from ._base import RdfBaseModel, RdfProperty


class OdrlResource(RdfBaseModel):
    """Base class for ODRL resources."""

    rdf_namespace: ClassVar = ODRL2  # type: ignore[assignment]
    rdf_prefixes: ClassVar = {"odrl": ODRL2}  # type: ignore[dict-item]


class Policy(OdrlResource):
    """An ODRL Policy."""

    rdf_type: ClassVar[str] = str(ODRL2.Policy)

    # Core policy properties
    uid: Annotated[list[str | URIRef] | None, RdfProperty(ODRL2.uid)] = None
    profile: Annotated[list[str | URIRef] | None, RdfProperty(ODRL2.profile)] = None

    # Rules
    permission: Annotated[list[str | URIRef | Permission] | None, RdfProperty(ODRL2.permission)] = None
    prohibition: Annotated[list[str | URIRef | Prohibition] | None, RdfProperty(ODRL2.prohibition)] = None
    obligation: Annotated[list[str | URIRef | Duty] | None, RdfProperty(ODRL2.obligation)] = None

    # Inheritance
    inherits_from: Annotated[list[str | URIRef | Policy] | None, RdfProperty(ODRL2.inheritFrom)] = None
    conflict: Annotated[list[str | URIRef | ConflictTerm] | None, RdfProperty(ODRL2.conflict)] = None


class Set(Policy):
    """An ODRL Set Policy - no specific target."""

    rdf_type: ClassVar[str] = str(ODRL2.Set)


class Offer(Policy):
    """An ODRL Offer - a policy offered by an assigner."""

    rdf_type: ClassVar[str] = str(ODRL2.Offer)


class Agreement(Policy):
    """An ODRL Agreement - a policy that has been agreed to."""

    rdf_type: ClassVar[str] = str(ODRL2.Agreement)


class Rule(OdrlResource):
    """Base class for ODRL Rules."""

    # Target
    target: Annotated[list[str | URIRef] | None, RdfProperty(ODRL2.target)] = None

    # Action
    action: Annotated[list[str | URIRef | Action] | None, RdfProperty(ODRL2.action)] = None

    # Parties
    assigner: Annotated[list[str | URIRef | Party] | None, RdfProperty(ODRL2.assigner)] = None
    assignee: Annotated[list[str | URIRef | Party] | None, RdfProperty(ODRL2.assignee)] = None

    # Constraints
    constraint: Annotated[list[str | URIRef | Constraint] | None, RdfProperty(ODRL2.constraint)] = None

    # Relations
    relation: Annotated[list[str | URIRef] | None, RdfProperty(ODRL2.relation)] = None
    function: Annotated[list[str | URIRef] | None, RdfProperty(ODRL2["function"])] = None
    failure: Annotated[list[str | URIRef | Rule] | None, RdfProperty(ODRL2.failure)] = None


class Permission(Rule):
    """An ODRL Permission - the ability to perform an action."""

    rdf_type: ClassVar[str] = str(ODRL2.Permission)

    # Duties
    duty: Annotated[list[str | URIRef | Duty] | None, RdfProperty(ODRL2.duty)] = None


class Prohibition(Rule):
    """An ODRL Prohibition - the inability to perform an action."""

    rdf_type: ClassVar[str] = str(ODRL2.Prohibition)

    # Remedies
    remedy: Annotated[list[str | URIRef | Duty] | None, RdfProperty(ODRL2.remedy)] = None


class Duty(Rule):
    """An ODRL Duty - an obligation to perform an action."""

    rdf_type: ClassVar[str] = str(ODRL2.Duty)

    # Consequences
    consequence: Annotated[list[str | URIRef | Duty] | None, RdfProperty(ODRL2.consequence)] = None


class Action(OdrlResource):
    """An ODRL Action - an operation on an asset."""

    rdf_type: ClassVar[str] = str(ODRL2.Action)

    # Action refinement
    refinement: Annotated[list[str | URIRef | Constraint] | None, RdfProperty(ODRL2.refinement)] = None
    implies: Annotated[list[str | URIRef | Action] | None, RdfProperty(ODRL2.implies)] = None


class Constraint(OdrlResource):
    """An ODRL Constraint - a boolean expression."""

    rdf_type: ClassVar[str] = str(ODRL2.Constraint)

    # Constraint properties
    left_operand: Annotated[list[str | URIRef] | None, RdfProperty(ODRL2.leftOperand)] = None
    operator: Annotated[list[str | URIRef] | None, RdfProperty(ODRL2.operator)] = None
    right_operand: Annotated[list[str | URIRef] | None, RdfProperty(ODRL2.rightOperand)] = None

    # Logical constraints
    and_sequence: Annotated[list[str | URIRef | Constraint] | None, RdfProperty(ODRL2["and"])] = None
    or_sequence: Annotated[list[str | URIRef | Constraint] | None, RdfProperty(ODRL2["or"])] = None
    xone: Annotated[list[str | URIRef | Constraint] | None, RdfProperty(ODRL2.xone)] = None

    # Data type
    data_type: Annotated[list[str | URIRef] | None, RdfProperty(ODRL2.dataType)] = None
    unit: Annotated[list[str | URIRef] | None, RdfProperty(ODRL2.unit)] = None
    status: Annotated[list[str] | None, RdfProperty(ODRL2.status)] = None


class Party(OdrlResource):
    """An ODRL Party - an entity with a functional role."""

    rdf_type: ClassVar[str] = str(ODRL2.Party)

    # Party refinement
    refinement: Annotated[list[str | URIRef | Constraint] | None, RdfProperty(ODRL2.refinement)] = None

    # Party scope
    part_of: Annotated[list[str | URIRef | PartyCollection] | None, RdfProperty(ODRL2.partOf)] = None
    source: Annotated[list[str | URIRef] | None, RdfProperty(ODRL2.source)] = None
    scope: Annotated[list[str | URIRef] | None, RdfProperty(ODRL2.scope)] = None


class PartyCollection(OdrlResource):
    """An ODRL Party Collection - a group of parties."""

    rdf_type: ClassVar[str] = str(ODRL2.PartyCollection)


class Asset(OdrlResource):
    """An ODRL Asset - a resource that is the subject of a policy."""

    rdf_type: ClassVar[str] = str(ODRL2.Asset)

    # Asset refinement
    refinement: Annotated[list[str | URIRef | Constraint] | None, RdfProperty(ODRL2.refinement)] = None

    # Asset scope
    part_of: Annotated[list[str | URIRef | AssetCollection] | None, RdfProperty(ODRL2.partOf)] = None
    source: Annotated[list[str | URIRef] | None, RdfProperty(ODRL2.source)] = None
    has_policy: Annotated[list[str | URIRef | Policy] | None, RdfProperty(ODRL2.hasPolicy)] = None


class AssetCollection(OdrlResource):
    """An ODRL Asset Collection - a group of assets."""

    rdf_type: ClassVar[str] = str(ODRL2.AssetCollection)


class Privacy(Policy):
    """An ODRL Privacy Policy."""

    rdf_type: ClassVar[str] = str(ODRL2.Privacy)


class Ticket(Policy):
    """An ODRL Ticket."""

    rdf_type: ClassVar[str] = str(ODRL2.Ticket)


class Assertion(Policy):
    """An ODRL Assertion."""

    rdf_type: ClassVar[str] = str(ODRL2.Assertion)


class Request(Policy):
    """An ODRL Request."""

    rdf_type: ClassVar[str] = str(ODRL2.Request)


class ConflictTerm(OdrlResource):
    """Conflict strategy preference."""

    rdf_type: ClassVar[str] = str(ODRL2.ConflictTerm)


class LogicalConstraint(OdrlResource):
    """A logical constraint."""

    rdf_type: ClassVar[str] = str(ODRL2.LogicalConstraint)


class LeftOperand(OdrlResource):
    """Left operand for a constraint."""

    rdf_type: ClassVar[str] = str(ODRL2.LeftOperand)


class RightOperand(OdrlResource):
    """Right operand for a constraint."""

    rdf_type: ClassVar[str] = str(ODRL2.RightOperand)


class Operator(OdrlResource):
    """Operator for a constraint."""

    rdf_type: ClassVar[str] = str(ODRL2.Operator)


__all__ = [
    "OdrlResource",
    "Policy",
    "Set",
    "Offer",
    "Agreement",
    "Privacy",
    "Ticket",
    "Assertion",
    "Request",
    "Rule",
    "Permission",
    "Prohibition",
    "Duty",
    "Action",
    "Constraint",
    "LogicalConstraint",
    "Party",
    "PartyCollection",
    "Asset",
    "AssetCollection",
    "ConflictTerm",
    "LeftOperand",
    "RightOperand",
    "Operator",
]
