from typing import Annotated, Optional, List, ClassVar
from rdflib import Namespace, URIRef, BNode, Graph
import uuid
from dartfx.rdf.pydantic import RdfBaseModel, RdfProperty

EX = Namespace("http://example.org/")

class Address(RdfBaseModel):
    rdf_type = EX.Address
    rdf_namespace = EX
    
    id: Optional[str] = None
    city: Annotated[Optional[str], RdfProperty(EX.city)] = None
    street: Annotated[Optional[str], RdfProperty(EX.street)] = None

class Person(RdfBaseModel):
    rdf_type = EX.Person
    rdf_namespace = EX
    
    id: Optional[str] = None
    name: Annotated[Optional[str], RdfProperty(EX.name)] = None
    address: Annotated[Optional[Address], RdfProperty(EX.address)] = None

class NestedAddress(Address):
    # Disable auto UUID generation for this subclass
    rdf_auto_uuid = False

class NestedPerson(Person):
    rdf_auto_uuid = False
    # Use NestedAddress for the address field
    address: Annotated[Optional[NestedAddress], RdfProperty(EX.address)] = None


def test_default_behavior():
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

def test_nested_behavior():
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
    assert "[" in turtle and "]" in turtle  # Basic check for nested structure in Turtle

def test_manual_id_override():
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

def test_top_level_bnode():
    """Test serialization of a top-level object without ID and auto_uuid=False."""
    addr = NestedAddress(city="Paris")
    graph = addr.to_rdf_graph()
    
    subjects = list(graph.subjects(predicate=EX.city, object=None))
    assert len(subjects) == 1
    assert isinstance(subjects[0], BNode)
