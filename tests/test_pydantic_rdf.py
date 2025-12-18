from __future__ import annotations

from typing import Annotated, Optional

from pydantic import Field
from rdflib import Literal, Namespace, RDF, URIRef

from dartfx.rdf.pydantic import RdfBaseModel, RdfProperty


SCHEMA = Namespace("https://schema.org/")
EX = Namespace("https://example.org/")
EX_PERSON = Namespace("https://example.org/person/")
EX_ADDRESS = Namespace("https://example.org/address/")


class Address(RdfBaseModel):
    rdf_type = SCHEMA.PostalAddress
    rdf_namespace = EX_ADDRESS
    rdf_prefixes = {"schema": SCHEMA, "ex": EX}

    id: str
    street: Annotated[str, RdfProperty(SCHEMA.streetAddress)]
    locality: Annotated[str, RdfProperty(SCHEMA.addressLocality)]
    country: Annotated[str, RdfProperty(SCHEMA.addressCountry)]


class Person(RdfBaseModel):
    rdf_type = SCHEMA.Person
    rdf_namespace = EX_PERSON
    rdf_prefixes = {"schema": SCHEMA, "ex": EX}

    id: str
    name: Annotated[str, RdfProperty(SCHEMA.name)]
    email: Annotated[Optional[str], RdfProperty(SCHEMA.email)] = None
    homepage: Annotated[Optional[str], RdfProperty(SCHEMA.url)] = None
    address: Annotated[Optional[Address], RdfProperty(SCHEMA.address)] = None
    knows: Annotated[Optional[list["Person"]], RdfProperty(SCHEMA.knows)] = Field(default_factory=list)


Person.model_rebuild()


def build_person() -> Person:
    home_address = Address(
        id="addr-1",
        street="123 Example Rd",
        locality="Examplesville",
        country="Wonderland",
    )
    friend_address = Address(
        id="addr-2",
        street="456 Side St",
        locality="Examplesville",
        country="Wonderland",
    )
    friend = Person(
        id="person-2",
        name="Bob",
        email="bob@example.org",
        homepage="https://example.org/bob",
        address=friend_address,
    )
    return Person(
        id="person-1",
        name="Alice",
        email="alice@example.org",
        homepage="https://example.org/alice",
        address=home_address,
        knows=[friend],
    )


def test_pydantic_model_serialisation() -> None:
    person = build_person()
    graph = person.to_rdf_graph()

    person_subject = URIRef(str(EX_PERSON) + person.id)
    friend_subject = URIRef(str(EX_PERSON) + person.knows[0].id)
    address_subject = URIRef(str(EX_ADDRESS) + person.address.id)

    assert (person_subject, RDF.type, SCHEMA.Person) in graph
    assert (person_subject, SCHEMA.name, Literal(person.name)) in graph
    assert (person_subject, SCHEMA.knows, friend_subject) in graph
    assert (person_subject, SCHEMA.address, address_subject) in graph
    assert (address_subject, RDF.type, SCHEMA.PostalAddress) in graph

    ttl = person.to_rdf(format="turtle")
    xml_data = person.to_rdf(format="xml")
    assert "Alice" in ttl
    assert "rdf:RDF" in xml_data


def test_pydantic_model_round_trip() -> None:
    person = build_person()
    graph = person.to_rdf_graph()

    subject = URIRef(str(EX_PERSON) + person.id)
    reloaded = Person.from_rdf_graph(graph, subject)

    assert reloaded.model_dump() == person.model_dump()

    ttl = person.to_rdf(format="turtle")
    reloaded_from_text = Person.from_rdf(ttl, format="turtle", subject=subject)

    assert reloaded_from_text.model_dump() == person.model_dump()

def test_turtle_01() -> None:
    person1 = Person(id="person-1", name="Alice")
    person2 = Person(id="person-2", name="Bob")
    graph = person1.to_rdf_graph()
    person2.to_rdf_graph(graph)
    ttl = graph.serialize(format="turtle")
    assert "Alice" in ttl
    assert "Bob" in ttl
    print("\n"+ttl)
    

def test_custom_uri_generator_01() -> None:
    def custom_uri_generator(obj: Any) -> Union[URIRef, BNode]:
        type = type(obj)
        return EX[f"{type.__name__}/{obj.id}"]
        
    person = build_person()
    graph = person.to_rdf_graph(rdf_uri_generator=custom_uri_generator)
    ttl = graph.serialize(format="turtle")
    assert "Alice" in ttl
    assert "Bob" in ttl
    print("\n"+ttl)
