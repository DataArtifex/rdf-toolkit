"""PROV (Provenance Ontology) vocabulary using Pydantic RDF models.

This module provides Pydantic-based models for the PROV-O vocabulary,
allowing easy serialization to and from RDF formats.

References:
- https://www.w3.org/TR/prov-o/
- https://www.w3.org/TR/prov-dm/

"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, ClassVar

from rdflib import PROV, URIRef

from ._base import RdfBaseModel, RdfProperty


class ProvResource(RdfBaseModel):
    """Base class for PROV resources."""

    rdf_namespace: ClassVar = PROV  # type: ignore[assignment]
    rdf_prefixes: ClassVar = {"prov": PROV}  # type: ignore[dict-item]


class Entity(ProvResource):
    """A PROV Entity - a physical, digital, conceptual, or other kind of thing."""

    rdf_type: ClassVar[str | URIRef | None] = str(PROV.Entity)

    # Generation and invalidation
    was_generated_by: Annotated[list[str | URIRef | Activity] | None, RdfProperty(PROV.wasGeneratedBy)] = None
    was_invalidated_by: Annotated[list[str | URIRef | Activity] | None, RdfProperty(PROV.wasInvalidatedBy)] = None
    generated_at_time: Annotated[list[str | datetime] | None, RdfProperty(PROV.generatedAtTime)] = None
    invalidated_at_time: Annotated[list[str | datetime] | None, RdfProperty(PROV.invalidatedAtTime)] = None

    # Derivation
    was_derived_from: Annotated[list[str | URIRef | Entity] | None, RdfProperty(PROV.wasDerivedFrom)] = None
    was_revision_of: Annotated[list[str | URIRef | Entity] | None, RdfProperty(PROV.wasRevisionOf)] = None
    was_quoted_from: Annotated[list[str | URIRef | Entity] | None, RdfProperty(PROV.wasQuotedFrom)] = None
    had_primary_source: Annotated[list[str | URIRef | Entity] | None, RdfProperty(PROV.hadPrimarySource)] = None

    # Attribution
    was_attributed_to: Annotated[list[str | URIRef | Agent] | None, RdfProperty(PROV.wasAttributedTo)] = None

    # Alternates and specialization
    alternate_of: Annotated[list[str | URIRef | Entity] | None, RdfProperty(PROV.alternateOf)] = None
    specialization_of: Annotated[list[str | URIRef | Entity] | None, RdfProperty(PROV.specializationOf)] = None

    # Location
    at_location: Annotated[list[str | URIRef | Location] | None, RdfProperty(PROV.atLocation)] = None

    # Value
    value: Annotated[list[str] | None, RdfProperty(PROV.value)] = None

    # Influence
    was_influenced_by: Annotated[
        list[str | URIRef | Agent | Entity | Activity | Influence] | None,
        RdfProperty(PROV.wasInfluencedBy),
    ] = None


class Activity(ProvResource):
    """A PROV Activity - something that occurs over a period of time."""

    rdf_type: ClassVar[str | URIRef | None] = str(PROV.Activity)

    # Timing
    started_at_time: Annotated[list[str | datetime] | None, RdfProperty(PROV.startedAtTime)] = None
    ended_at_time: Annotated[list[str | datetime] | None, RdfProperty(PROV.endedAtTime)] = None

    # Usage and generation
    used: Annotated[list[str | URIRef | Entity] | None, RdfProperty(PROV.used)] = None
    generated: Annotated[list[str | URIRef | Entity] | None, RdfProperty(PROV.generated)] = None
    invalidated: Annotated[list[str | URIRef | Entity] | None, RdfProperty(PROV.invalidated)] = None

    # Association
    was_associated_with: Annotated[list[str | URIRef | Agent] | None, RdfProperty(PROV.wasAssociatedWith)] = None
    qualified_association: Annotated[
        list[str | URIRef | Association] | None, RdfProperty(PROV.qualifiedAssociation)
    ] = None

    # Communication
    was_informed_by: Annotated[list[str | URIRef | Activity] | None, RdfProperty(PROV.wasInformedBy)] = None

    # Start and end
    was_started_by: Annotated[list[str | URIRef | Entity] | None, RdfProperty(PROV.wasStartedBy)] = None
    was_ended_by: Annotated[list[str | URIRef | Entity] | None, RdfProperty(PROV.wasEndedBy)] = None

    # Location
    at_location: Annotated[list[str | URIRef | Location] | None, RdfProperty(PROV.atLocation)] = None

    # Influence
    was_influenced_by: Annotated[
        list[str | URIRef | Agent | Entity | Activity | Influence] | None,
        RdfProperty(PROV.wasInfluencedBy),
    ] = None


class Agent(ProvResource):
    """A PROV Agent - something that bears some form of responsibility."""

    rdf_type: ClassVar[str | URIRef | None] = str(PROV.Agent)

    # Agency relationships
    acted_on_behalf_of: Annotated[list[str | URIRef | Agent] | None, RdfProperty(PROV.actedOnBehalfOf)] = None
    qualified_delegation: Annotated[list[str | URIRef | Delegation] | None, RdfProperty(PROV.qualifiedDelegation)] = (
        None
    )

    # Location
    at_location: Annotated[list[str | URIRef | Location] | None, RdfProperty(PROV.atLocation)] = None

    # Influence
    was_influenced_by: Annotated[
        list[str | URIRef | Agent | Entity | Activity | Influence] | None,
        RdfProperty(PROV.wasInfluencedBy),
    ] = None


class Person(Agent):
    """A PROV Person."""

    rdf_type: ClassVar[str | URIRef | None] = str(PROV.Person)


class Organization(Agent):
    """A PROV Organization."""

    rdf_type: ClassVar[str | URIRef | None] = str(PROV.Organization)


class SoftwareAgent(Agent):
    """A PROV Software Agent."""

    rdf_type: ClassVar[str | URIRef | None] = str(PROV.SoftwareAgent)


class Bundle(Entity):
    """A PROV Bundle - a named set of provenance descriptions."""

    rdf_type: ClassVar[str | URIRef | None] = str(PROV.Bundle)


class Collection(Entity):
    """A PROV Collection - an entity that provides a structure for its members."""

    rdf_type: ClassVar[str | URIRef | None] = str(PROV.Collection)

    had_member: Annotated[list[str | URIRef | Entity] | None, RdfProperty(PROV.hadMember)] = None


class Plan(Entity):
    """A PROV Plan - a set of actions or steps intended by an agent."""

    rdf_type: ClassVar[str | URIRef | None] = str(PROV.Plan)


class Association(ProvResource):
    """A PROV Association - an assignment of responsibility to an agent."""

    rdf_type: ClassVar[str | URIRef | None] = str(PROV.Association)

    agent: Annotated[list[str | URIRef | Agent] | None, RdfProperty(PROV.agent)] = None
    had_plan: Annotated[list[str | URIRef | Plan] | None, RdfProperty(PROV.hadPlan)] = None
    had_role: Annotated[list[str | URIRef | Role] | None, RdfProperty(PROV.hadRole)] = None


class Delegation(ProvResource):
    """A PROV Delegation - responsibility transfer from one agent to another."""

    rdf_type: ClassVar[str | URIRef | None] = str(PROV.Delegation)

    agent: Annotated[list[str | URIRef | Agent] | None, RdfProperty(PROV.agent)] = None
    had_activity: Annotated[list[str | URIRef | Activity] | None, RdfProperty(PROV.hadActivity)] = None
    had_role: Annotated[list[str | URIRef | Role] | None, RdfProperty(PROV.hadRole)] = None


class Usage(ProvResource):
    """A PROV Usage - consumption of an entity by an activity."""

    rdf_type: ClassVar[str | URIRef | None] = str(PROV.Usage)

    entity: Annotated[list[str | URIRef | Entity] | None, RdfProperty(PROV.entity)] = None
    had_role: Annotated[list[str | URIRef | Role] | None, RdfProperty(PROV.hadRole)] = None
    at_time: Annotated[list[str | datetime] | None, RdfProperty(PROV.atTime)] = None


class Generation(ProvResource):
    """A PROV Generation - completion of production of a new entity."""

    rdf_type: ClassVar[str | URIRef | None] = str(PROV.Generation)

    entity: Annotated[list[str | URIRef | Entity] | None, RdfProperty(PROV.entity)] = None
    activity: Annotated[list[str | URIRef | Activity] | None, RdfProperty(PROV.activity)] = None
    had_role: Annotated[list[str | URIRef | Role] | None, RdfProperty(PROV.hadRole)] = None
    at_time: Annotated[list[str | datetime] | None, RdfProperty(PROV.atTime)] = None


class Derivation(ProvResource):
    """A PROV Derivation - transformation of an entity into another."""

    rdf_type: ClassVar[str | URIRef | None] = str(PROV.Derivation)

    entity: Annotated[list[str | URIRef | Entity] | None, RdfProperty(PROV.entity)] = None
    had_generation: Annotated[list[str | URIRef | Generation] | None, RdfProperty(PROV.hadGeneration)] = None
    had_usage: Annotated[list[str | URIRef | Usage] | None, RdfProperty(PROV.hadUsage)] = None
    had_activity: Annotated[list[str | URIRef | Activity] | None, RdfProperty(PROV.hadActivity)] = None


class Role(ProvResource):
    """A PROV Role - function of an entity or agent in an activity."""

    rdf_type: ClassVar[str | URIRef | None] = str(PROV.Role)


class Influence(ProvResource):
    """A PROV Influence - capacity of an entity, activity, or agent to have an effect on another."""

    rdf_type: ClassVar[str | URIRef | None] = str(PROV.Influence)

    influencer: Annotated[
        list[str | URIRef | Agent | Entity | Activity] | None,
        RdfProperty(PROV.influencer),
    ] = None
    had_role: Annotated[list[str | URIRef | Role] | None, RdfProperty(PROV.hadRole)] = None
    had_activity: Annotated[list[str | URIRef | Activity] | None, RdfProperty(PROV.hadActivity)] = None
    had_plan: Annotated[list[str | URIRef | Plan] | None, RdfProperty(PROV.hadPlan)] = None
    had_usage: Annotated[list[str | URIRef | Usage] | None, RdfProperty(PROV.hadUsage)] = None
    had_generation: Annotated[list[str | URIRef | Generation] | None, RdfProperty(PROV.hadGeneration)] = None


class InstantaneousEvent(ProvResource):
    """A PROV Instantaneous Event - happens at a specific instant in time."""

    rdf_type: ClassVar[str | URIRef | None] = str(PROV.InstantaneousEvent)

    at_time: Annotated[list[str | datetime] | None, RdfProperty(PROV.atTime)] = None
    had_role: Annotated[list[str | URIRef | Role] | None, RdfProperty(PROV.hadRole)] = None
    at_location: Annotated[list[str | URIRef | Location] | None, RdfProperty(PROV.atLocation)] = None


class Location(ProvResource):
    """A PROV Location - an identifiable geographic place."""

    rdf_type: ClassVar[str | URIRef | None] = str(PROV.Location)


class End(InstantaneousEvent, Influence):
    """A PROV End - when an activity is deemed to have ended."""

    rdf_type: ClassVar[str | URIRef | None] = str(PROV.End)

    had_activity: Annotated[list[str | URIRef | Activity] | None, RdfProperty(PROV.hadActivity)] = None
    entity: Annotated[list[str | URIRef | Entity] | None, RdfProperty(PROV.entity)] = None


class Start(InstantaneousEvent, Influence):
    """A PROV Start - when an activity is deemed to have started."""

    rdf_type: ClassVar[str | URIRef | None] = str(PROV.Start)

    had_activity: Annotated[list[str | URIRef | Activity] | None, RdfProperty(PROV.hadActivity)] = None
    entity: Annotated[list[str | URIRef | Entity] | None, RdfProperty(PROV.entity)] = None


class EmptyCollection(Collection):
    """A PROV Empty Collection - a collection with no members."""

    rdf_type: ClassVar[str | URIRef | None] = str(PROV.EmptyCollection)


__all__ = [
    "ProvResource",
    "Entity",
    "Activity",
    "Agent",
    "Person",
    "Organization",
    "SoftwareAgent",
    "Bundle",
    "Collection",
    "Plan",
    "Association",
    "Delegation",
    "Usage",
    "Generation",
    "Derivation",
    "Role",
    "Influence",
    "InstantaneousEvent",
    "Location",
    "End",
    "Start",
    "EmptyCollection",
]
