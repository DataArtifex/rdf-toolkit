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

from dartfx.rdf.pydantic_rdf import RdfBaseModel, RdfProperty


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


class TelephoneType(VcardResource):
    """Telephone type classifications."""
    pass


class EmailType(VcardResource):
    """Email type classifications."""
    pass


class AddressType(VcardResource):
    """Address type classifications."""
    pass
