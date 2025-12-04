"""PROV (Provenance Ontology) vocabulary using Pydantic RDF models.

This module provides Pydantic-based models for the PROV-O vocabulary,
allowing easy serialization to and from RDF formats.

References:
- https://www.w3.org/TR/prov-o/
- https://www.w3.org/TR/prov-dm/

"""

from __future__ import annotations
from typing import Annotated, List, Optional
from datetime import datetime

from rdflib import URIRef, PROV

from .rdf import RdfBaseModel, RdfProperty


class ProvResource(RdfBaseModel):
    """Base class for PROV resources."""
    
    rdf_namespace = PROV
    rdf_prefixes = {"prov": PROV}


class Entity(ProvResource):
    """A PROV Entity - a physical, digital, conceptual, or other kind of thing."""
    
    rdf_type: str = str(PROV.Entity)
    
    # Generation and invalidation
    was_generated_by: Annotated[Optional[List[str | URIRef | Activity]], RdfProperty(PROV.wasGeneratedBy)] = None
    was_invalidated_by: Annotated[Optional[List[str | URIRef | Activity]], RdfProperty(PROV.wasInvalidatedBy)] = None
    generated_at_time: Annotated[Optional[List[str | datetime]], RdfProperty(PROV.generatedAtTime)] = None
    invalidated_at_time: Annotated[Optional[List[str | datetime]], RdfProperty(PROV.invalidatedAtTime)] = None
    
    # Derivation
    was_derived_from: Annotated[Optional[List[str | URIRef | Entity]], RdfProperty(PROV.wasDerivedFrom)] = None
    was_revision_of: Annotated[Optional[List[str | URIRef | Entity]], RdfProperty(PROV.wasRevisionOf)] = None
    was_quoted_from: Annotated[Optional[List[str | URIRef | Entity]], RdfProperty(PROV.wasQuotedFrom)] = None
    had_primary_source: Annotated[Optional[List[str | URIRef | Entity]], RdfProperty(PROV.hadPrimarySource)] = None
    
    # Attribution
    was_attributed_to: Annotated[Optional[List[str | URIRef | Agent]], RdfProperty(PROV.wasAttributedTo)] = None
    
    # Alternates and specialization
    alternate_of: Annotated[Optional[List[str | URIRef | Entity]], RdfProperty(PROV.alternateOf)] = None
    specialization_of: Annotated[Optional[List[str | URIRef | Entity]], RdfProperty(PROV.specializationOf)] = None
    
    # Location
    at_location: Annotated[Optional[List[str | URIRef | Location]], RdfProperty(PROV.atLocation)] = None
    
    # Value
    value: Annotated[Optional[List[str]], RdfProperty(PROV.value)] = None
    
    # Influence
    was_influenced_by: Annotated[Optional[List[str | URIRef | Agent | Entity | Activity | Influence]], RdfProperty(PROV.wasInfluencedBy)] = None


class Activity(ProvResource):
    """A PROV Activity - something that occurs over a period of time."""
    
    rdf_type: str = str(PROV.Activity)
    
    # Timing
    started_at_time: Annotated[Optional[List[str | datetime]], RdfProperty(PROV.startedAtTime)] = None
    ended_at_time: Annotated[Optional[List[str | datetime]], RdfProperty(PROV.endedAtTime)] = None
    
    # Usage and generation
    used: Annotated[Optional[List[str | URIRef | Entity]], RdfProperty(PROV.used)] = None
    generated: Annotated[Optional[List[str | URIRef | Entity]], RdfProperty(PROV.generated)] = None
    invalidated: Annotated[Optional[List[str | URIRef | Entity]], RdfProperty(PROV.invalidated)] = None
    
    # Association
    was_associated_with: Annotated[Optional[List[str | URIRef | Agent]], RdfProperty(PROV.wasAssociatedWith)] = None
    qualified_association: Annotated[Optional[List[str | URIRef | Association]], RdfProperty(PROV.qualifiedAssociation)] = None
    
    # Communication
    was_informed_by: Annotated[Optional[List[str | URIRef | Activity]], RdfProperty(PROV.wasInformedBy)] = None
    
    # Start and end
    was_started_by: Annotated[Optional[List[str | URIRef | Entity]], RdfProperty(PROV.wasStartedBy)] = None
    was_ended_by: Annotated[Optional[List[str | URIRef | Entity]], RdfProperty(PROV.wasEndedBy)] = None
    
    # Location
    at_location: Annotated[Optional[List[str | URIRef | Location]], RdfProperty(PROV.atLocation)] = None
    
    # Influence
    was_influenced_by: Annotated[Optional[List[str | URIRef | Agent | Entity | Activity | Influence]], RdfProperty(PROV.wasInfluencedBy)] = None


class Agent(ProvResource):
    """A PROV Agent - something that bears some form of responsibility."""
    
    rdf_type: str = str(PROV.Agent)
    
    # Agency relationships
    acted_on_behalf_of: Annotated[Optional[List[str | URIRef | Agent]], RdfProperty(PROV.actedOnBehalfOf)] = None
    qualified_delegation: Annotated[Optional[List[str | URIRef | Delegation]], RdfProperty(PROV.qualifiedDelegation)] = None
    
    # Location
    at_location: Annotated[Optional[List[str | URIRef | Location]], RdfProperty(PROV.atLocation)] = None
    
    # Influence
    was_influenced_by: Annotated[Optional[List[str | URIRef | Agent | Entity | Activity | Influence]], RdfProperty(PROV.wasInfluencedBy)] = None


class Person(Agent):
    """A PROV Person."""
    
    rdf_type: str = str(PROV.Person)


class Organization(Agent):
    """A PROV Organization."""
    
    rdf_type: str = str(PROV.Organization)


class SoftwareAgent(Agent):
    """A PROV Software Agent."""
    
    rdf_type: str = str(PROV.SoftwareAgent)


class Bundle(Entity):
    """A PROV Bundle - a named set of provenance descriptions."""
    
    rdf_type: str = str(PROV.Bundle)


class Collection(Entity):
    """A PROV Collection - an entity that provides a structure for its members."""
    
    rdf_type: str = str(PROV.Collection)
    
    had_member: Annotated[Optional[List[str | URIRef | Entity]], RdfProperty(PROV.hadMember)] = None


class Plan(Entity):
    """A PROV Plan - a set of actions or steps intended by an agent."""
    
    rdf_type: str = str(PROV.Plan)


class Association(ProvResource):
    """A PROV Association - an assignment of responsibility to an agent."""
    
    rdf_type: str = str(PROV.Association)
    
    agent: Annotated[Optional[List[str | URIRef | Agent]], RdfProperty(PROV.agent)] = None
    had_plan: Annotated[Optional[List[str | URIRef | Plan]], RdfProperty(PROV.hadPlan)] = None
    had_role: Annotated[Optional[List[str | URIRef | Role]], RdfProperty(PROV.hadRole)] = None


class Delegation(ProvResource):
    """A PROV Delegation - responsibility transfer from one agent to another."""
    
    rdf_type: str = str(PROV.Delegation)
    
    agent: Annotated[Optional[List[str | URIRef | Agent]], RdfProperty(PROV.agent)] = None
    had_activity: Annotated[Optional[List[str | URIRef | Activity]], RdfProperty(PROV.hadActivity)] = None
    had_role: Annotated[Optional[List[str | URIRef | Role]], RdfProperty(PROV.hadRole)] = None


class Usage(ProvResource):
    """A PROV Usage - consumption of an entity by an activity."""
    
    rdf_type: str = str(PROV.Usage)
    
    entity: Annotated[Optional[List[str | URIRef | Entity]], RdfProperty(PROV.entity)] = None
    had_role: Annotated[Optional[List[str | URIRef | Role]], RdfProperty(PROV.hadRole)] = None
    at_time: Annotated[Optional[List[str | datetime]], RdfProperty(PROV.atTime)] = None


class Generation(ProvResource):
    """A PROV Generation - completion of production of a new entity."""
    
    rdf_type: str = str(PROV.Generation)
    
    entity: Annotated[Optional[List[str | URIRef | Entity]], RdfProperty(PROV.entity)] = None
    activity: Annotated[Optional[List[str | URIRef | Activity]], RdfProperty(PROV.activity)] = None
    had_role: Annotated[Optional[List[str | URIRef | Role]], RdfProperty(PROV.hadRole)] = None
    at_time: Annotated[Optional[List[str | datetime]], RdfProperty(PROV.atTime)] = None


class Derivation(ProvResource):
    """A PROV Derivation - transformation of an entity into another."""
    
    rdf_type: str = str(PROV.Derivation)
    
    entity: Annotated[Optional[List[str | URIRef | Entity]], RdfProperty(PROV.entity)] = None
    had_generation: Annotated[Optional[List[str | URIRef | Generation]], RdfProperty(PROV.hadGeneration)] = None
    had_usage: Annotated[Optional[List[str | URIRef | Usage]], RdfProperty(PROV.hadUsage)] = None
    had_activity: Annotated[Optional[List[str | URIRef | Activity]], RdfProperty(PROV.hadActivity)] = None


class Role(ProvResource):
    """A PROV Role - function of an entity or agent in an activity."""
    
    rdf_type: str = str(PROV.Role)
class Influence(ProvResource):
    """A PROV Influence - capacity of an entity, activity, or agent to have an effect on another."""
    
    rdf_type: str = str(PROV.Influence)
    
    influencer: Annotated[Optional[List[str | URIRef | Agent | Entity | Activity]], RdfProperty(PROV.influencer)] = None
    had_role: Annotated[Optional[List[str | URIRef | Role]], RdfProperty(PROV.hadRole)] = None
    had_activity: Annotated[Optional[List[str | URIRef | Activity]], RdfProperty(PROV.hadActivity)] = None
    had_plan: Annotated[Optional[List[str | URIRef | Plan]], RdfProperty(PROV.hadPlan)] = None
    had_usage: Annotated[Optional[List[str | URIRef | Usage]], RdfProperty(PROV.hadUsage)] = None
    had_generation: Annotated[Optional[List[str | URIRef | Generation]], RdfProperty(PROV.hadGeneration)] = None


class InstantaneousEvent(ProvResource):
    """A PROV Instantaneous Event - happens at a specific instant in time."""
    
    rdf_type: str = str(PROV.InstantaneousEvent)
    
    at_time: Annotated[Optional[List[str | datetime]], RdfProperty(PROV.atTime)] = None
    had_role: Annotated[Optional[List[str | URIRef | Role]], RdfProperty(PROV.hadRole)] = None
    at_location: Annotated[Optional[List[str | URIRef | Location]], RdfProperty(PROV.atLocation)] = None


class Location(ProvResource):
    """A PROV Location - an identifiable geographic place."""
    
    rdf_type: str = str(PROV.Location)


class End(InstantaneousEvent, Influence):
    """A PROV End - when an activity is deemed to have ended."""
    
    rdf_type: str = str(PROV.End)
    
    had_activity: Annotated[Optional[List[str | URIRef | Activity]], RdfProperty(PROV.hadActivity)] = None
    entity: Annotated[Optional[List[str | URIRef | Entity]], RdfProperty(PROV.entity)] = None


class Start(InstantaneousEvent, Influence):
    """A PROV Start - when an activity is deemed to have started."""
    
    rdf_type: str = str(PROV.Start)
    
    had_activity: Annotated[Optional[List[str | URIRef | Activity]], RdfProperty(PROV.hadActivity)] = None
    entity: Annotated[Optional[List[str | URIRef | Entity]], RdfProperty(PROV.entity)] = None


class EmptyCollection(Collection):
    """A PROV Empty Collection - a collection with no members."""
    
    rdf_type: str = str(PROV.EmptyCollection)


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

