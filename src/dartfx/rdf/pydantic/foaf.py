"""FOAF (Friend of a Friend) vocabulary using Pydantic RDF models.

This module provides Pydantic-based models for the FOAF vocabulary,
allowing easy serialization to and from RDF formats.

References:
- http://xmlns.com/foaf/spec/

"""

from __future__ import annotations
from typing import Annotated, List, Optional

from rdflib import URIRef, FOAF

from ._base import RdfBaseModel, RdfProperty


class FoafResource(RdfBaseModel):
    """Base class for FOAF resources."""
    
    rdf_namespace = FOAF
    rdf_prefixes = {"foaf": FOAF}


class Agent(FoafResource):
    """An agent (person, group, software or physical artifact)."""
    
    rdf_type: str = str(FOAF.Agent)
    
    # Naming properties
    name: Annotated[Optional[List[str]], RdfProperty(FOAF.name)] = None
    nick: Annotated[Optional[List[str]], RdfProperty(FOAF.nick)] = None
    title: Annotated[Optional[List[str]], RdfProperty(FOAF.title)] = None
    
    # Contact properties
    mbox: Annotated[Optional[List[str | URIRef]], RdfProperty(FOAF.mbox)] = None
    homepage: Annotated[Optional[List[str | URIRef]], RdfProperty(FOAF.homepage)] = None
    weblog: Annotated[Optional[List[str | URIRef]], RdfProperty(FOAF.weblog)] = None
    
    # Account properties
    account: Annotated[Optional[List[str | URIRef | OnlineAccount]], RdfProperty(FOAF.account)] = None
    
    # Other properties
    made: Annotated[Optional[List[str | URIRef]], RdfProperty(FOAF.made)] = None
    img: Annotated[Optional[List[str | URIRef]], RdfProperty(FOAF.img)] = None
    depiction: Annotated[Optional[List[str | URIRef]], RdfProperty(FOAF.depiction)] = None

    # Chat IDs
    aim_chat_id: Annotated[Optional[List[str]], RdfProperty(FOAF.aimChatID)] = None
    icq_chat_id: Annotated[Optional[List[str]], RdfProperty(FOAF.icqChatID)] = None
    yahoo_chat_id: Annotated[Optional[List[str]], RdfProperty(FOAF.yahooChatID)] = None
    msn_chat_id: Annotated[Optional[List[str]], RdfProperty(FOAF.msnChatID)] = None
    jabber_id: Annotated[Optional[List[str]], RdfProperty(FOAF.jabberID)] = None
    
    # Other
    tipjar: Annotated[Optional[List[str | URIRef]], RdfProperty(FOAF.tipjar)] = None
    status: Annotated[Optional[List[str]], RdfProperty(FOAF.status)] = None


class Person(Agent):
    """A person."""
    
    rdf_type: str = str(FOAF.Person)
    
    # Personal info
    given_name: Annotated[Optional[List[str]], RdfProperty(FOAF.givenName)] = None
    family_name: Annotated[Optional[List[str]], RdfProperty(FOAF.familyName)] = None
    first_name: Annotated[Optional[List[str]], RdfProperty(FOAF.firstName)] = None
    surname: Annotated[Optional[List[str]], RdfProperty(FOAF.surname)] = None
    
    # Demographics
    gender: Annotated[Optional[List[str]], RdfProperty(FOAF.gender)] = None
    birthday: Annotated[Optional[List[str]], RdfProperty(FOAF.birthday)] = None
    age: Annotated[Optional[List[str]], RdfProperty(FOAF.age)] = None
    
    # Relationships
    knows: Annotated[Optional[List[str | URIRef | Person]], RdfProperty(FOAF.knows)] = None
    
    # Work/Organization
    based_near: Annotated[Optional[List[str | URIRef]], RdfProperty(FOAF.based_near)] = None
    current_project: Annotated[Optional[List[str | URIRef]], RdfProperty(FOAF.currentProject)] = None
    past_project: Annotated[Optional[List[str | URIRef]], RdfProperty(FOAF.pastProject)] = None
    publications: Annotated[Optional[List[str | URIRef]], RdfProperty(FOAF.publications)] = None
    
    # Online presence
    openid: Annotated[Optional[List[str | URIRef]], RdfProperty(FOAF.openid)] = None
    
    # Extended properties
    geekcode: Annotated[Optional[List[str]], RdfProperty(FOAF.geekcode)] = None
    myers_briggs: Annotated[Optional[List[str]], RdfProperty(FOAF.myersBriggs)] = None
    plan: Annotated[Optional[List[str]], RdfProperty(FOAF.plan)] = None
    dna_checksum: Annotated[Optional[List[str]], RdfProperty(FOAF.dnaChecksum)] = None
    workplace_homepage: Annotated[Optional[List[str | URIRef]], RdfProperty(FOAF.workplaceHomepage)] = None
    work_info_homepage: Annotated[Optional[List[str | URIRef]], RdfProperty(FOAF.workInfoHomepage)] = None
    school_homepage: Annotated[Optional[List[str | URIRef]], RdfProperty(FOAF.schoolHomepage)] = None
    interest: Annotated[Optional[List[str | URIRef | Document]], RdfProperty(FOAF.interest)] = None
    topic_interest: Annotated[Optional[List[str | URIRef]], RdfProperty(FOAF.topic_interest)] = None
    last_name: Annotated[Optional[List[str]], RdfProperty(FOAF.lastName)] = None


class Organization(Agent):
    """An organization."""
    
    rdf_type: str = str(FOAF.Organization)
    
    # Organization relationships
    member: Annotated[Optional[List[str | URIRef | Agent]], RdfProperty(FOAF.member)] = None


class Group(Agent):
    """A group of agents."""
    
    rdf_type: str = str(FOAF.Group)
    
    # Group membership
    member: Annotated[Optional[List[str | URIRef | Agent]], RdfProperty(FOAF.member)] = None


class Document(FoafResource):
    """A document."""
    
    rdf_type: str = str(FOAF.Document)
    
    topic: Annotated[Optional[List[str | URIRef]], RdfProperty(FOAF.topic)] = None
    primary_topic: Annotated[Optional[List[str | URIRef]], RdfProperty(FOAF.primaryTopic)] = None


class Image(Document):
    """An image."""
    
    rdf_type: str = str(FOAF.Image)
    
    depicts: Annotated[Optional[List[str | URIRef]], RdfProperty(FOAF.depicts)] = None
    thumbnail: Annotated[Optional[List[str | URIRef]], RdfProperty(FOAF.thumbnail)] = None


class OnlineAccount(FoafResource):
    """An online account."""
    
    rdf_type: str = str(FOAF.OnlineAccount)
    
    account_name: Annotated[Optional[List[str]], RdfProperty(FOAF.accountName)] = None
    account_service_homepage: Annotated[Optional[List[str | URIRef]], RdfProperty(FOAF.accountServiceHomepage)] = None


class OnlineChatAccount(OnlineAccount):
    """An online chat account."""
    
    rdf_type: str = str(FOAF.OnlineChatAccount)


class OnlineEcommerceAccount(OnlineAccount):
    """An online e-commerce account."""
    
    rdf_type: str = str(FOAF.OnlineEcommerceAccount)


class OnlineGamingAccount(OnlineAccount):
    """An online gaming account."""
    
    rdf_type: str = str(FOAF.OnlineGamingAccount)


class PersonalProfileDocument(Document):
    """A personal profile document."""
    
    rdf_type: str = str(FOAF.PersonalProfileDocument)


class Project(FoafResource):
    """A project (a collective endeavour of some kind)."""
    
    rdf_type: str = str(FOAF.Project)
    
    name: Annotated[Optional[List[str]], RdfProperty(FOAF.name)] = None
    homepage: Annotated[Optional[List[str | URIRef]], RdfProperty(FOAF.homepage)] = None
    logo: Annotated[Optional[List[str | URIRef]], RdfProperty(FOAF.logo)] = None
    funded_by: Annotated[Optional[List[str | URIRef | Agent]], RdfProperty(FOAF.fundedBy)] = None


class LabelProperty(FoafResource):
    """A label property."""
    
    rdf_type: str = str(FOAF.LabelProperty)





__all__ = [
    "FoafResource",
    "Agent",
    "Person",
    "Organization",
    "Group",
    "Document",
    "Image",
    "OnlineAccount",
    "OnlineChatAccount",
    "OnlineEcommerceAccount",
    "OnlineGamingAccount",
    "PersonalProfileDocument",
    "Project",
    "LabelProperty",
]
