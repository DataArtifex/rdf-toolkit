"""VCARD vocabulary using Pydantic RDF models.

This module provides Pydantic-based models for the vCard ontology,
allowing easy serialization to and from RDF formats.

References:
- https://www.w3.org/TR/vcard-rdf/
- https://www.w3.org/2006/vcard/ns

"""

from __future__ import annotations

from typing import Annotated, ClassVar

from rdflib import Namespace, URIRef

from ._base import RdfBaseModel, RdfProperty

# VCARD namespace (not built-in to rdflib)
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")


class VcardResource(RdfBaseModel):
    """Base class for vCard resources."""

    rdf_namespace: ClassVar = VCARD
    rdf_prefixes: ClassVar = {"vcard": VCARD}


class VCard(VcardResource):
    """A vCard - electronic business card."""

    rdf_type: ClassVar[str | URIRef | None] = str(VCARD.VCard)

    # Identification
    fn: Annotated[list[str] | None, RdfProperty(VCARD.fn)] = None  # Formatted name
    n: Annotated[list[str | URIRef | Name] | None, RdfProperty(VCARD.n)] = None  # Name
    nickname: Annotated[list[str] | None, RdfProperty(VCARD.nickname)] = None

    # Delivery address
    adr: Annotated[list[str | URIRef | Address] | None, RdfProperty(VCARD.adr)] = None

    # Telecommunications
    tel: Annotated[list[str | URIRef | Telephone] | None, RdfProperty(VCARD.tel)] = None
    email: Annotated[list[str | URIRef | Email] | None, RdfProperty(VCARD.email)] = None

    # Organization
    org: Annotated[list[str | URIRef | Organization] | None, RdfProperty(VCARD.org)] = None
    organization_name: Annotated[list[str] | None, RdfProperty(VCARD["organization-name"])] = None
    organization_unit: Annotated[list[str] | None, RdfProperty(VCARD["organization-unit"])] = None

    # Title and role
    title: Annotated[list[str] | None, RdfProperty(VCARD.title)] = None
    role: Annotated[list[str] | None, RdfProperty(VCARD.role)] = None

    # Online presence
    url: Annotated[list[str | URIRef] | None, RdfProperty(VCARD.url)] = None

    # Birthday
    bday: Annotated[list[str] | None, RdfProperty(VCARD.bday)] = None

    # Photo
    photo: Annotated[list[str | URIRef] | None, RdfProperty(VCARD.photo)] = None
    logo: Annotated[list[str | URIRef] | None, RdfProperty(VCARD.logo)] = None

    # Categories
    category: Annotated[list[str] | None, RdfProperty(VCARD.category)] = None

    # Notes
    note: Annotated[list[str] | None, RdfProperty(VCARD.note)] = None

    # Revision
    rev: Annotated[list[str] | None, RdfProperty(VCARD.rev)] = None

    # UID
    uid: Annotated[list[str | URIRef] | None, RdfProperty(VCARD.uid)] = None

    # Language
    language: Annotated[list[str] | None, RdfProperty(VCARD.language)] = None

    # New properties
    has_gender: Annotated[list[str | URIRef | Gender] | None, RdfProperty(VCARD.hasGender)] = None
    has_related: Annotated[list[str | URIRef | Related] | None, RdfProperty(VCARD.hasRelated)] = None
    has_geo: Annotated[list[str | URIRef | Location] | None, RdfProperty(VCARD.hasGeo)] = None
    has_sound: Annotated[list[str | URIRef] | None, RdfProperty(VCARD.hasSound)] = None
    has_key: Annotated[list[str | URIRef] | None, RdfProperty(VCARD.hasKey)] = None
    has_logo: Annotated[list[str | URIRef] | None, RdfProperty(VCARD.hasLogo)] = None
    has_photo: Annotated[list[str | URIRef] | None, RdfProperty(VCARD.hasPhoto)] = None
    has_url: Annotated[list[str | URIRef] | None, RdfProperty(VCARD.hasUrl)] = None
    has_email: Annotated[list[str | URIRef | Email] | None, RdfProperty(VCARD.hasEmail)] = None
    has_telephone: Annotated[list[str | URIRef | Telephone] | None, RdfProperty(VCARD.hasTelephone)] = None
    has_note: Annotated[list[str] | None, RdfProperty(VCARD.hasNote)] = None
    has_uid: Annotated[list[str | URIRef] | None, RdfProperty(VCARD.hasUID)] = None
    has_language: Annotated[list[str] | None, RdfProperty(VCARD.hasLanguage)] = None


class Individual(VCard):
    """An individual person."""

    rdf_type: ClassVar[str | URIRef | None] = str(VCARD.Individual)


class Group(VCard):
    """A group of persons or entities."""

    rdf_type: ClassVar[str | URIRef | None] = str(VCARD.Group)

    has_member: Annotated[list[str | URIRef | VCard] | None, RdfProperty(VCARD.hasMember)] = None


class Organization(VCard):
    """An organization."""

    rdf_type: ClassVar[str | URIRef | None] = str(VCARD.Organization)


class Location(VCard):
    """A location."""

    rdf_type: ClassVar[str | URIRef | None] = str(VCARD.Location)


class Name(VcardResource):
    """A name component."""

    rdf_type: ClassVar[str | URIRef | None] = str(VCARD.Name)

    family_name: Annotated[list[str] | None, RdfProperty(VCARD["family-name"])] = None
    given_name: Annotated[list[str] | None, RdfProperty(VCARD["given-name"])] = None
    additional_name: Annotated[list[str] | None, RdfProperty(VCARD["additional-name"])] = None
    honorific_prefix: Annotated[list[str] | None, RdfProperty(VCARD["honorific-prefix"])] = None
    honorific_suffix: Annotated[list[str] | None, RdfProperty(VCARD["honorific-suffix"])] = None


class Address(VcardResource):
    """A delivery address."""

    rdf_type: ClassVar[str | URIRef | None] = str(VCARD.Address)

    street_address: Annotated[list[str] | None, RdfProperty(VCARD["street-address"])] = None
    locality: Annotated[list[str] | None, RdfProperty(VCARD.locality)] = None
    region: Annotated[list[str] | None, RdfProperty(VCARD.region)] = None
    postal_code: Annotated[list[str] | None, RdfProperty(VCARD["postal-code"])] = None
    country_name: Annotated[list[str] | None, RdfProperty(VCARD["country-name"])] = None
    post_office_box: Annotated[list[str] | None, RdfProperty(VCARD["post-office-box"])] = None
    extended_address: Annotated[list[str] | None, RdfProperty(VCARD["extended-address"])] = None


class Telephone(VcardResource):
    """A telephone number."""

    rdf_type: ClassVar[str | URIRef | None] = str(VCARD.Telephone)

    has_value: Annotated[list[str | URIRef] | None, RdfProperty(VCARD.hasValue)] = None


class Email(VcardResource):
    """An email address."""

    rdf_type: ClassVar[str | URIRef | None] = str(VCARD.Email)

    has_value: Annotated[list[str | URIRef] | None, RdfProperty(VCARD.hasValue)] = None


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

    rdf_type: ClassVar[str | URIRef | None] = str(VCARD.Gender)

    sex: Annotated[list[str] | None, RdfProperty(VCARD.sex)] = None
    identity: Annotated[list[str] | None, RdfProperty(VCARD.identity)] = None


class Related(VcardResource):
    """A related entity."""

    rdf_type: ClassVar[str | URIRef | None] = str(VCARD.Related)

    has_value: Annotated[list[str | URIRef | VCard] | None, RdfProperty(VCARD.hasValue)] = None


class Acquaintance(Related):
    """An acquaintance."""

    rdf_type: ClassVar[str | URIRef | None] = str(VCARD.Acquaintance)


class Friend(Related):
    """A friend."""

    rdf_type: ClassVar[str | URIRef | None] = str(VCARD.Friend)


class Parent(Related):
    """A parent."""

    rdf_type: ClassVar[str | URIRef | None] = str(VCARD.Parent)


class Child(Related):
    """A child."""

    rdf_type: ClassVar[str | URIRef | None] = str(VCARD.Child)


class Spouse(Related):
    """A spouse."""

    rdf_type: ClassVar[str | URIRef | None] = str(VCARD.Spouse)


class Sibling(Related):
    """A sibling."""

    rdf_type: ClassVar[str | URIRef | None] = str(VCARD.Sibling)


class Kin(Related):
    """A kin."""

    rdf_type: ClassVar[str | URIRef | None] = str(VCARD.Kin)


class Colleague(Related):
    """A colleague."""

    rdf_type: ClassVar[str | URIRef | None] = str(VCARD.Colleague)


class Emergency(Related):
    """An emergency contact."""

    rdf_type: ClassVar[str | URIRef | None] = str(VCARD.Emergency)


class Agent(Related):
    """An agent."""

    rdf_type: ClassVar[str | URIRef | None] = str(VCARD.Agent)


class CoResident(Related):
    """A co-resident."""

    rdf_type: ClassVar[str | URIRef | None] = str(VCARD.CoResident)


class Neighbor(Related):
    """A neighbor."""

    rdf_type: ClassVar[str | URIRef | None] = str(VCARD.Neighbor)


class Coworker(Related):
    """A coworker."""

    rdf_type: ClassVar[str | URIRef | None] = str(VCARD.Coworker)


class Kind(VcardResource):
    """A kind of vCard."""

    rdf_type: ClassVar[str | URIRef | None] = str(VCARD.Kind)


class Type(VcardResource):
    """A property type."""

    rdf_type: ClassVar[str | URIRef | None] = str(VCARD.Type)
