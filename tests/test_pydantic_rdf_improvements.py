from __future__ import annotations

import uuid
from decimal import Decimal, InvalidOperation
from typing import Annotated, Optional

import pytest
from rdflib import Namespace, URIRef, XSD, Literal

from dartfx.rdf.pydantic.rdf import RdfBaseModel, RdfProperty, _unique, _node_to_python

EX = Namespace("https://example.org/")

class DataTypesModel(RdfBaseModel):
    rdf_type = EX.DataTypes
    rdf_namespace = EX
    
    id: str
    uuid_val: Annotated[Optional[uuid.UUID], RdfProperty(EX.uuid)] = None
    bytes_val: Annotated[Optional[bytes], RdfProperty(EX.bytes)] = None
    decimal_val: Annotated[Optional[Decimal], RdfProperty(EX.decimal)] = None

def test_unique_preserves_order_and_uniqueness():
    input_list = [1, 2, 3, 2, 1, 4, 5, 5]
    expected = [1, 2, 3, 4, 5]
    assert _unique(input_list) == expected

def test_unique_with_rdflib_terms():
    t1 = URIRef("http://example.org/1")
    t2 = URIRef("http://example.org/2")
    t3 = Literal("foo")
    
    input_list = [t1, t2, t1, t3, t2]
    expected = [t1, t2, t3]
    assert _unique(input_list) == expected

def test_datatypes_round_trip():
    uid = uuid.uuid4()
    byte_data = b"hello world"
    dec = Decimal("123.456")
    
    model = DataTypesModel(
        id="dt-1",
        uuid_val=uid,
        bytes_val=byte_data,
        decimal_val=dec
    )
    
    # Serialize
    graph = model.to_rdf_graph()
    
    # Verify triples
    subject = URIRef(str(EX) + "dt-1")
    
    # UUID should be string
    assert (subject, EX.uuid, Literal(str(uid), datatype=XSD.string)) in graph
    
    # Bytes should be base64Binary
    # Note: rdflib might handle bytes automatically if we map it to XSD.base64Binary
    # Let's see how our implementation handles it.
    
    # Deserialize
    reloaded = DataTypesModel.from_rdf_graph(graph, subject)
    
    assert reloaded.uuid_val == uid
    assert reloaded.bytes_val == byte_data
    assert reloaded.decimal_val == dec

def test_decimal_error_handling():
    # Test that invalid decimal strings don't crash but return the string or raise appropriate error
    # The current implementation returns the value if conversion fails.
    # We want to ensure we catch specific exceptions.
    
    prop = RdfProperty(EX.decimal)
    node = Literal("not-a-decimal")
    
    # Depending on implementation, this might return "not-a-decimal" or raise validation error later
    # Our _node_to_python should return the value if conversion fails, 
    # but Pydantic validation will likely catch it.
    
    # Let's test _node_to_python directly
    val = _node_to_python(node, Decimal, prop)
    assert val == "not-a-decimal"

