"""FOAF (Friend of a Friend) vocabulary using Pydantic RDF models.

This module provides Pydantic-based models for the FOAF vocabulary,
allowing easy serialization to and from RDF formats.

References:
- http://xmlns.com/foaf/spec/

"""

from __future__ import annotations

from typing import Annotated, ClassVar

from rdflib import FOAF, URIRef

from ._base import RdfBaseModel, RdfProperty


class FoafResource(RdfBaseModel):
    """Base class for FOAF resources."""

    rdf_namespace: ClassVar = FOAF  # type: ignore[assignment]
    rdf_prefixes: ClassVar = {"foaf": FOAF}  # type: ignore[dict-item]


class Agent(FoafResource):
    """An agent (person, group, software or physical artifact)."""

    rdf_type: ClassVar[str | URIRef | None] = str(FOAF.Agent)

    # Naming properties
    name: Annotated[str | list[str] | None, RdfProperty(FOAF.name)] = None
    nick: Annotated[str | list[str] | None, RdfProperty(FOAF.nick)] = None
    title: Annotated[str | list[str] | None, RdfProperty(FOAF.title)] = None

    # Contact properties
    mbox: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(FOAF.mbox)] = None
    homepage: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(FOAF.homepage)] = None
    weblog: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(FOAF.weblog)] = None

    # Account properties
    account: Annotated[
        str | URIRef | OnlineAccount | list[str | URIRef | OnlineAccount] | None,
        RdfProperty(FOAF.account),
    ] = None

    # Other properties
    made: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(FOAF.made)] = None
    img: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(FOAF.img)] = None
    depiction: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(FOAF.depiction)] = None

    # Chat IDs
    aim_chat_id: Annotated[str | list[str] | None, RdfProperty(FOAF.aimChatID)] = None
    icq_chat_id: Annotated[str | list[str] | None, RdfProperty(FOAF.icqChatID)] = None
    yahoo_chat_id: Annotated[str | list[str] | None, RdfProperty(FOAF.yahooChatID)] = None
    msn_chat_id: Annotated[str | list[str] | None, RdfProperty(FOAF.msnChatID)] = None
    jabber_id: Annotated[str | list[str] | None, RdfProperty(FOAF.jabberID)] = None

    # Other
    tipjar: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(FOAF.tipjar)] = None
    status: Annotated[str | list[str] | None, RdfProperty(FOAF.status)] = None


class Person(Agent):
    """A person."""

    rdf_type: ClassVar[str | URIRef | None] = str(FOAF.Person)

    # Personal info
    given_name: Annotated[str | list[str] | None, RdfProperty(FOAF.givenName)] = None
    family_name: Annotated[str | list[str] | None, RdfProperty(FOAF.familyName)] = None
    first_name: Annotated[str | list[str] | None, RdfProperty(FOAF.firstName)] = None
    surname: Annotated[str | list[str] | None, RdfProperty(FOAF.surname)] = None

    # Demographics
    gender: Annotated[str | list[str] | None, RdfProperty(FOAF.gender)] = None
    birthday: Annotated[str | list[str] | None, RdfProperty(FOAF.birthday)] = None
    age: Annotated[str | list[str] | None, RdfProperty(FOAF.age)] = None

    # Relationships
    knows: Annotated[str | URIRef | Person | list[str | URIRef | Person] | None, RdfProperty(FOAF.knows)] = None

    # Work/Organization
    based_near: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(FOAF.based_near)] = None
    current_project: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(FOAF.currentProject)] = None
    past_project: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(FOAF.pastProject)] = None
    publications: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(FOAF.publications)] = None

    # Online presence
    openid: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(FOAF.openid)] = None

    # Extended properties
    geekcode: Annotated[str | list[str] | None, RdfProperty(FOAF.geekcode)] = None
    myers_briggs: Annotated[str | list[str] | None, RdfProperty(FOAF.myersBriggs)] = None
    plan: Annotated[str | list[str] | None, RdfProperty(FOAF.plan)] = None
    dna_checksum: Annotated[str | list[str] | None, RdfProperty(FOAF.dnaChecksum)] = None
    workplace_homepage: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(FOAF.workplaceHomepage)] = None
    work_info_homepage: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(FOAF.workInfoHomepage)] = None
    school_homepage: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(FOAF.schoolHomepage)] = None
    interest: Annotated[
        str | URIRef | Document | list[str | URIRef | Document] | None,
        RdfProperty(FOAF.interest),
    ] = None
    topic_interest: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(FOAF.topic_interest)] = None
    last_name: Annotated[str | list[str] | None, RdfProperty(FOAF.lastName)] = None


class Organization(Agent):
    """An organization."""

    rdf_type: ClassVar[str | URIRef | None] = str(FOAF.Organization)

    # Organization relationships
    member: Annotated[str | URIRef | Agent | list[str | URIRef | Agent] | None, RdfProperty(FOAF.member)] = None


class Group(Agent):
    """A group of agents."""

    rdf_type: ClassVar[str | URIRef | None] = str(FOAF.Group)

    # Group membership
    member: Annotated[str | URIRef | Agent | list[str | URIRef | Agent] | None, RdfProperty(FOAF.member)] = None


class Document(FoafResource):
    """A document."""

    rdf_type: ClassVar[str | URIRef | None] = str(FOAF.Document)

    topic: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(FOAF.topic)] = None
    primary_topic: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(FOAF.primaryTopic)] = None


class Image(Document):
    """An image."""

    rdf_type: ClassVar[str | URIRef | None] = str(FOAF.Image)

    depicts: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(FOAF.depicts)] = None
    thumbnail: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(FOAF.thumbnail)] = None


class OnlineAccount(FoafResource):
    """An online account."""

    rdf_type: ClassVar[str | URIRef | None] = str(FOAF.OnlineAccount)

    account_name: Annotated[str | list[str] | None, RdfProperty(FOAF.accountName)] = None
    account_service_homepage: Annotated[
        str | URIRef | list[str | URIRef] | None,
        RdfProperty(FOAF.accountServiceHomepage),
    ] = None


class OnlineChatAccount(OnlineAccount):
    """An online chat account."""

    rdf_type: ClassVar[str | URIRef | None] = str(FOAF.OnlineChatAccount)


class OnlineEcommerceAccount(OnlineAccount):
    """An online e-commerce account."""

    rdf_type: ClassVar[str | URIRef | None] = str(FOAF.OnlineEcommerceAccount)


class OnlineGamingAccount(OnlineAccount):
    """An online gaming account."""

    rdf_type: ClassVar[str | URIRef | None] = str(FOAF.OnlineGamingAccount)


class PersonalProfileDocument(Document):
    """A personal profile document."""

    rdf_type: ClassVar[str | URIRef | None] = str(FOAF.PersonalProfileDocument)


class Project(FoafResource):
    """A project (a collective endeavour of some kind)."""

    rdf_type: ClassVar[str | URIRef | None] = str(FOAF.Project)

    name: Annotated[str | list[str] | None, RdfProperty(FOAF.name)] = None
    homepage: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(FOAF.homepage)] = None
    logo: Annotated[str | URIRef | list[str | URIRef] | None, RdfProperty(FOAF.logo)] = None
    funded_by: Annotated[str | URIRef | Agent | list[str | URIRef | Agent] | None, RdfProperty(FOAF.fundedBy)] = None


class LabelProperty(FoafResource):
    """A label property."""

    rdf_type: ClassVar[str | URIRef | None] = str(FOAF.LabelProperty)


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
