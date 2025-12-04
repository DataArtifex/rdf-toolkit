"""VCARD vocabulary using Pydantic RDF models.

This module provides Pydantic-based models for the vCard ontology,
allowing easy serialization to and from RDF formats.

References:
- https://www.w3.org/TR/vcard-rdf/
- https://www.w3.org/2006/vcard/ns

"""

from __future__ import annotations
from typing import Annotated, List, Optional

from rdflib import Namespace, URIRef

from .rdf import RdfBaseModel, RdfProperty


# VCARD namespace (not built-in to rdflib)
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")


class VcardResource(RdfBaseModel):
    """Base class for vCard resources."""
    
    rdf_namespace = VCARD
    rdf_prefixes = {"vcard": VCARD}


class VCard(VcardResource):
    """A vCard - electronic business card."""
    
    rdf_type: str = str(VCARD.VCard)
    
    # Identification
    fn: Annotated[Optional[List[str]], RdfProperty(VCARD.fn)] = None  # Formatted name
    n: Annotated[Optional[List[str | URIRef | Name]], RdfProperty(VCARD.n)] = None  # Name
    nickname: Annotated[Optional[List[str]], RdfProperty(VCARD.nickname)] = None
    
    # Delivery address
    adr: Annotated[Optional[List[str | URIRef | Address]], RdfProperty(VCARD.adr)] = None
    
    # Telecommunications
    tel: Annotated[Optional[List[str | URIRef | Telephone]], RdfProperty(VCARD.tel)] = None
    email: Annotated[Optional[List[str | URIRef | Email]], RdfProperty(VCARD.email)] = None
    
    # Organization
    org: Annotated[Optional[List[str | URIRef | Organization]], RdfProperty(VCARD.org)] = None
    organization_name: Annotated[Optional[List[str]], RdfProperty(VCARD["organization-name"])] = None
    organization_unit: Annotated[Optional[List[str]], RdfProperty(VCARD["organization-unit"])] = None
    
    # Title and role
    title: Annotated[Optional[List[str]], RdfProperty(VCARD.title)] = None
    role: Annotated[Optional[List[str]], RdfProperty(VCARD.role)] = None
    
    # Online presence
    url: Annotated[Optional[List[str | URIRef]], RdfProperty(VCARD.url)] = None
    
    # Birthday
    bday: Annotated[Optional[List[str]], RdfProperty(VCARD.bday)] = None
    
    # Photo
    photo: Annotated[Optional[List[str | URIRef]], RdfProperty(VCARD.photo)] = None
    logo: Annotated[Optional[List[str | URIRef]], RdfProperty(VCARD.logo)] = None
    
    # Categories
    category: Annotated[Optional[List[str]], RdfProperty(VCARD.category)] = None
    
    # Notes
    note: Annotated[Optional[List[str]], RdfProperty(VCARD.note)] = None
    
    # Revision
    rev: Annotated[Optional[List[str]], RdfProperty(VCARD.rev)] = None
    
    # UID
    uid: Annotated[Optional[List[str | URIRef]], RdfProperty(VCARD.uid)] = None
    
    # Language
    language: Annotated[Optional[List[str]], RdfProperty(VCARD.language)] = None
    
    # New properties
    has_gender: Annotated[Optional[List[str | URIRef | Gender]], RdfProperty(VCARD.hasGender)] = None
    has_related: Annotated[Optional[List[str | URIRef | Related]], RdfProperty(VCARD.hasRelated)] = None
    has_geo: Annotated[Optional[List[str | URIRef | Location]], RdfProperty(VCARD.hasGeo)] = None
    has_sound: Annotated[Optional[List[str | URIRef]], RdfProperty(VCARD.hasSound)] = None
    has_key: Annotated[Optional[List[str | URIRef]], RdfProperty(VCARD.hasKey)] = None
    has_logo: Annotated[Optional[List[str | URIRef]], RdfProperty(VCARD.hasLogo)] = None
    has_photo: Annotated[Optional[List[str | URIRef]], RdfProperty(VCARD.hasPhoto)] = None
    has_url: Annotated[Optional[List[str | URIRef]], RdfProperty(VCARD.hasUrl)] = None
    has_email: Annotated[Optional[List[str | URIRef | Email]], RdfProperty(VCARD.hasEmail)] = None
    has_telephone: Annotated[Optional[List[str | URIRef | Telephone]], RdfProperty(VCARD.hasTelephone)] = None
    has_note: Annotated[Optional[List[str]], RdfProperty(VCARD.hasNote)] = None
    has_uid: Annotated[Optional[List[str | URIRef]], RdfProperty(VCARD.hasUID)] = None
    has_language: Annotated[Optional[List[str]], RdfProperty(VCARD.hasLanguage)] = None


class Individual(VCard):
    """An individual person."""
    
    rdf_type: str = str(VCARD.Individual)


class Group(VCard):
    """A group of persons or entities."""
    
    rdf_type: str = str(VCARD.Group)
    
    has_member: Annotated[Optional[List[str | URIRef | VCard]], RdfProperty(VCARD.hasMember)] = None


class Organization(VCard):
    """An organization."""
    
    rdf_type: str = str(VCARD.Organization)


class Location(VCard):
    """A location."""
    
    rdf_type: str = str(VCARD.Location)


class Name(VcardResource):
    """A name component."""
    
    rdf_type: str = str(VCARD.Name)
    
    family_name: Annotated[Optional[List[str]], RdfProperty(VCARD["family-name"])] = None
    given_name: Annotated[Optional[List[str]], RdfProperty(VCARD["given-name"])] = None
    additional_name: Annotated[Optional[List[str]], RdfProperty(VCARD["additional-name"])] = None
    honorific_prefix: Annotated[Optional[List[str]], RdfProperty(VCARD["honorific-prefix"])] = None
    honorific_suffix: Annotated[Optional[List[str]], RdfProperty(VCARD["honorific-suffix"])] = None


class Address(VcardResource):
    """A delivery address."""
    
    rdf_type: str = str(VCARD.Address)
    
    street_address: Annotated[Optional[List[str]], RdfProperty(VCARD["street-address"])] = None
    locality: Annotated[Optional[List[str]], RdfProperty(VCARD.locality)] = None
    region: Annotated[Optional[List[str]], RdfProperty(VCARD.region)] = None
    postal_code: Annotated[Optional[List[str]], RdfProperty(VCARD["postal-code"])] = None
    country_name: Annotated[Optional[List[str]], RdfProperty(VCARD["country-name"])] = None
    post_office_box: Annotated[Optional[List[str]], RdfProperty(VCARD["post-office-box"])] = None
    extended_address: Annotated[Optional[List[str]], RdfProperty(VCARD["extended-address"])] = None


class Telephone(VcardResource):
    """A telephone number."""
    
    rdf_type: str = str(VCARD.Telephone)
    
    has_value: Annotated[Optional[List[str | URIRef]], RdfProperty(VCARD.hasValue)] = None


class Email(VcardResource):
    """An email address."""
    
    rdf_type: str = str(VCARD.Email)
    
    has_value: Annotated[Optional[List[str | URIRef]], RdfProperty(VCARD.hasValue)] = None

__all__ = [
    "VcardResource",
    "VCard",
    "Individual",
    "Group",
    "Organization",
    "Location",
    "Name",
    "Address",
    "Telephone",
    "Email",
    "TelephoneType",
    "EmailType",
    "AddressType",
    "Gender",
    "Related",
    "Acquaintance",
    "Friend",
    "Parent",
    "Child",
    "Spouse",
    "Sibling",
    "Kin",
    "Colleague",
    "Emergency",
    "Agent",
    "CoResident",
    "Neighbor",
    "Coworker",
    "Kind",
    "Type",
]


class TelephoneType(VcardResource):
    """Telephone type classifications."""
    pass


class EmailType(VcardResource):
    """Email type classifications."""
    pass


class AddressType(VcardResource):
    """Address type classifications."""
    pass


class Gender(VcardResource):
    """A gender."""
    
    rdf_type: str = str(VCARD.Gender)
    
    sex: Annotated[Optional[List[str]], RdfProperty(VCARD.sex)] = None
    identity: Annotated[Optional[List[str]], RdfProperty(VCARD.identity)] = None


class Related(VcardResource):
    """A related entity."""
    
    rdf_type: str = str(VCARD.Related)
    
    has_value: Annotated[Optional[List[str | URIRef | VCard]], RdfProperty(VCARD.hasValue)] = None


class Acquaintance(Related):
    """An acquaintance."""
    rdf_type: str = str(VCARD.Acquaintance)


class Friend(Related):
    """A friend."""
    rdf_type: str = str(VCARD.Friend)


class Parent(Related):
    """A parent."""
    rdf_type: str = str(VCARD.Parent)


class Child(Related):
    """A child."""
    rdf_type: str = str(VCARD.Child)


class Spouse(Related):
    """A spouse."""
    rdf_type: str = str(VCARD.Spouse)


class Sibling(Related):
    """A sibling."""
    rdf_type: str = str(VCARD.Sibling)


class Kin(Related):
    """A kin."""
    rdf_type: str = str(VCARD.Kin)


class Colleague(Related):
    """A colleague."""
    rdf_type: str = str(VCARD.Colleague)


class Emergency(Related):
    """An emergency contact."""
    rdf_type: str = str(VCARD.Emergency)


class Agent(Related):
    """An agent."""
    rdf_type: str = str(VCARD.Agent)


class CoResident(Related):
    """A co-resident."""
    rdf_type: str = str(VCARD.CoResident)


class Neighbor(Related):
    """A neighbor."""
    rdf_type: str = str(VCARD.Neighbor)


class Coworker(Related):
    """A coworker."""
    rdf_type: str = str(VCARD.Coworker)


class Kind(VcardResource):
    """A kind of vCard."""
    rdf_type: str = str(VCARD.Kind)


class Type(VcardResource):
    """A property type."""
    rdf_type: str = str(VCARD.Type)

