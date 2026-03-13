from typing import Annotated, ClassVar

from rdflib import BNode, Namespace, URIRef

from dartfx.rdf.pydantic import DefaultUriGenerator, RdfBaseModel, RdfProperty

EX = Namespace("http://example.org/")


class Address(RdfBaseModel):
    rdf_type: ClassVar = EX.Address
    rdf_namespace: ClassVar = EX

    id: str | None = None
    city: Annotated[str | None, RdfProperty(EX.city)] = None
    street: Annotated[str | None, RdfProperty(EX.street)] = None


class Person(RdfBaseModel):
    rdf_type: ClassVar = EX.Person
    rdf_namespace: ClassVar = EX

    id: str | None = None
    name: Annotated[str | None, RdfProperty(EX.name)] = None
    address: Annotated[Address | None, RdfProperty(EX.address)] = None


class NestedAddress(Address):
    # Disable auto UUID generation for this subclass
    rdf_uri_generator: DefaultUriGenerator = DefaultUriGenerator(auto_uuid=False)


class NestedPerson(Person):
    rdf_uri_generator: DefaultUriGenerator = DefaultUriGenerator(auto_uuid=False)
    # Use NestedAddress for the address field
    address: Annotated[NestedAddress | None, RdfProperty(EX.address)] = None


def test_default_behavior() -> None:
    """Test that default behavior (auto UUID) is preserved."""
    addr = Address(city="London", street="10 Downing St")
    person = Person(id="alice", name="Alice", address=addr)

    graph = person.to_rdf_graph()

    # Check that address has a UUID URI
    person_uri = URIRef(str(EX) + "alice")
    addresses = list(graph.objects(person_uri, EX.address))
    assert len(addresses) == 1
    assert isinstance(addresses[0], URIRef)
    assert str(addresses[0]).startswith(str(EX)) or str(addresses[0]).startswith("urn:uuid:")


def test_nested_behavior() -> None:
    """Test that disabling auto UUID produces BNodes (nested serialization)."""
    addr = NestedAddress(city="London", street="10 Downing St")
    person = NestedPerson(id="bob", name="Bob", address=addr)

    graph = person.to_rdf_graph()

    # Check that address points to a BNode
    person_uri = URIRef(str(EX) + "bob")
    addresses = list(graph.objects(person_uri, EX.address))
    assert len(addresses) == 1
    assert isinstance(addresses[0], BNode)

    # Serialize to turtle and check content
    turtle = person.to_rdf("turtle")
    assert "[" in turtle  # Basic check for nested structure in Turtle
    assert "]" in turtle


def test_manual_id_override() -> None:
    """Test that providing an ID still produces a URI even if auto_uuid is False."""
    addr = NestedAddress(id="my-addr", city="London", street="10 Downing St")
    person = NestedPerson(id="charlie", name="Charlie", address=addr)

    graph = person.to_rdf_graph()

    person_uri = URIRef(str(EX) + "charlie")
    addresses = list(graph.objects(person_uri, EX.address))
    assert len(addresses) == 1
    assert isinstance(addresses[0], URIRef)
    # Depending on how _subject_uri is implemented, it might use the namespace or just the ID
    # Our implementation uses namespace + ID if namespace exists
    assert str(addresses[0]) == str(EX) + "my-addr"


def test_top_level_bnode() -> None:
    """Test serialization of a top-level object without ID and auto_uuid=False."""
    addr = NestedAddress(city="Paris")
    graph = addr.to_rdf_graph()

    subjects = list(graph.subjects(predicate=EX.city, object=None))
    assert len(subjects) == 1
    assert isinstance(subjects[0], BNode)


def test_union_type_nested_model_round_trip() -> None:
    """Ensure T | None union types work for nested models round-trip deserialization."""
    addr = Address(id="addr-1", city="Berlin", street="Champs")
    person = Person(id="david", name="David", address=addr)

    graph = person.to_rdf_graph()

    person_uri = URIRef(str(EX) + "david")
    reloaded = Person.from_rdf_graph(graph, person_uri)

    assert reloaded.id == "david"
    assert reloaded.name == "David"
    assert reloaded.address is not None
    assert isinstance(reloaded.address, Address)
    assert reloaded.address.id == "addr-1"
    assert reloaded.address.city == "Berlin"
    assert reloaded.address.street == "Champs"
