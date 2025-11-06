"""ODRL (Open Digital Rights Language) vocabulary using Pydantic RDF models.

This module provides Pydantic-based models for the ODRL vocabulary,
allowing easy serialization to and from RDF formats.

References:
- https://www.w3.org/TR/odrl-model/
- https://www.w3.org/TR/odrl-vocab/

"""

from __future__ import annotations
from typing import Annotated, List, Optional

from rdflib import URIRef, ODRL2

from dartfx.rdf.pydantic_rdf import RdfBaseModel, RdfProperty


class OdrlResource(RdfBaseModel):
    """Base class for ODRL resources."""
    
    rdf_namespace = ODRL2
    rdf_prefixes = {"odrl": ODRL2}


class Policy(OdrlResource):
    """An ODRL Policy."""
    
    rdf_type: str = str(ODRL2.Policy)
    
    # Core policy properties
    uid: Annotated[Optional[List[str | URIRef]], RdfProperty(ODRL2.uid)] = None
    profile: Annotated[Optional[List[str | URIRef]], RdfProperty(ODRL2.profile)] = None
    
    # Rules
    permission: Annotated[Optional[List[str | URIRef | Permission]], RdfProperty(ODRL2.permission)] = None
    prohibition: Annotated[Optional[List[str | URIRef | Prohibition]], RdfProperty(ODRL2.prohibition)] = None
    obligation: Annotated[Optional[List[str | URIRef | Duty]], RdfProperty(ODRL2.obligation)] = None
    
    # Inheritance
    inherits_from: Annotated[Optional[List[str | URIRef | Policy]], RdfProperty(ODRL2.inheritFrom)] = None


class Set(Policy):
    """An ODRL Set Policy - no specific target."""
    
    rdf_type: str = str(ODRL2.Set)


class Offer(Policy):
    """An ODRL Offer - a policy offered by an assigner."""
    
    rdf_type: str = str(ODRL2.Offer)


class Agreement(Policy):
    """An ODRL Agreement - a policy that has been agreed to."""
    
    rdf_type: str = str(ODRL2.Agreement)


class Rule(OdrlResource):
    """Base class for ODRL Rules."""
    
    # Target
    target: Annotated[Optional[List[str | URIRef]], RdfProperty(ODRL2.target)] = None
    
    # Action
    action: Annotated[Optional[List[str | URIRef | Action]], RdfProperty(ODRL2.action)] = None
    
    # Parties
    assigner: Annotated[Optional[List[str | URIRef | Party]], RdfProperty(ODRL2.assigner)] = None
    assignee: Annotated[Optional[List[str | URIRef | Party]], RdfProperty(ODRL2.assignee)] = None
    
    # Constraints
    constraint: Annotated[Optional[List[str | URIRef | Constraint]], RdfProperty(ODRL2.constraint)] = None
    
    # Relations
    relation: Annotated[Optional[List[str | URIRef]], RdfProperty(ODRL2.relation)] = None
    function: Annotated[Optional[List[str | URIRef]], RdfProperty(ODRL2["function"])] = None


class Permission(Rule):
    """An ODRL Permission - the ability to perform an action."""
    
    rdf_type: str = str(ODRL2.Permission)
    
    # Duties
    duty: Annotated[Optional[List[str | URIRef | Duty]], RdfProperty(ODRL2.duty)] = None


class Prohibition(Rule):
    """An ODRL Prohibition - the inability to perform an action."""
    
    rdf_type: str = str(ODRL2.Prohibition)
    
    # Remedies
    remedy: Annotated[Optional[List[str | URIRef | Duty]], RdfProperty(ODRL2.remedy)] = None


class Duty(Rule):
    """An ODRL Duty - an obligation to perform an action."""
    
    rdf_type: str = str(ODRL2.Duty)
    
    # Consequences
    consequence: Annotated[Optional[List[str | URIRef | Duty]], RdfProperty(ODRL2.consequence)] = None


class Action(OdrlResource):
    """An ODRL Action - an operation on an asset."""
    
    rdf_type: str = str(ODRL2.Action)
    
    # Action refinement
    refinement: Annotated[Optional[List[str | URIRef | Constraint]], RdfProperty(ODRL2.refinement)] = None
    implies: Annotated[Optional[List[str | URIRef | Action]], RdfProperty(ODRL2.implies)] = None


class Constraint(OdrlResource):
    """An ODRL Constraint - a boolean expression."""
    
    rdf_type: str = str(ODRL2.Constraint)
    
    # Constraint properties
    left_operand: Annotated[Optional[List[str | URIRef]], RdfProperty(ODRL2.leftOperand)] = None
    operator: Annotated[Optional[List[str | URIRef]], RdfProperty(ODRL2.operator)] = None
    right_operand: Annotated[Optional[List[str | URIRef]], RdfProperty(ODRL2.rightOperand)] = None
    
    # Logical constraints
    and_sequence: Annotated[Optional[List[str | URIRef | Constraint]], RdfProperty(ODRL2["and"])] = None
    or_sequence: Annotated[Optional[List[str | URIRef | Constraint]], RdfProperty(ODRL2["or"])] = None
    xone: Annotated[Optional[List[str | URIRef | Constraint]], RdfProperty(ODRL2.xone)] = None
    
    # Data type
    data_type: Annotated[Optional[List[str | URIRef]], RdfProperty(ODRL2.dataType)] = None
    unit: Annotated[Optional[List[str | URIRef]], RdfProperty(ODRL2.unit)] = None
    status: Annotated[Optional[List[str]], RdfProperty(ODRL2.status)] = None


class Party(OdrlResource):
    """An ODRL Party - an entity with a functional role."""
    
    rdf_type: str = str(ODRL2.Party)
    
    # Party refinement
    refinement: Annotated[Optional[List[str | URIRef | Constraint]], RdfProperty(ODRL2.refinement)] = None
    
    # Party scope
    part_of: Annotated[Optional[List[str | URIRef | PartyCollection]], RdfProperty(ODRL2.partOf)] = None
    source: Annotated[Optional[List[str | URIRef]], RdfProperty(ODRL2.source)] = None


class PartyCollection(OdrlResource):
    """An ODRL Party Collection - a group of parties."""
    
    rdf_type: str = str(ODRL2.PartyCollection)


class Asset(OdrlResource):
    """An ODRL Asset - a resource that is the subject of a policy."""
    
    rdf_type: str = str(ODRL2.Asset)
    
    # Asset refinement
    refinement: Annotated[Optional[List[str | URIRef | Constraint]], RdfProperty(ODRL2.refinement)] = None
    
    # Asset scope
    part_of: Annotated[Optional[List[str | URIRef | AssetCollection]], RdfProperty(ODRL2.partOf)] = None
    source: Annotated[Optional[List[str | URIRef]], RdfProperty(ODRL2.source)] = None


class AssetCollection(OdrlResource):
    """An ODRL Asset Collection - a group of assets."""
    
    rdf_type: str = str(ODRL2.AssetCollection)
