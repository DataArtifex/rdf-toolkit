"""Tests for multi-type support and dynamic type preservation in dartfx.rdf."""

from typing import Annotated, ClassVar

import pytest
from rdflib import RDF, Graph, Literal, Namespace, URIRef

from dartfx.rdf.pydantic import RdfBaseModel, RdfProperty

SCHEMA = Namespace("http://schema.org/")
CDI = Namespace("http://ddialliance.org/Specification/DDI-CDI/1.0/RDF/")
EX = Namespace("http://example.org/")


class MultiTypeItem(RdfBaseModel):
    rdf_type: ClassVar = [SCHEMA.PropertyValue, CDI.InstanceVariable]
    rdf_prefixes: ClassVar = {"schema": SCHEMA, "cdi": CDI, "ex": EX}

    id: str | None = None
    name: Annotated[str | None, RdfProperty(SCHEMA.name)] = None


class SingleTypeItem(RdfBaseModel):
    rdf_type: ClassVar = CDI.InstanceVariable
    rdf_prefixes: ClassVar = {"schema": SCHEMA, "cdi": CDI, "ex": EX}

    id: str | None = None
    name: Annotated[str | None, RdfProperty(SCHEMA.name)] = None


class StrictSingleTypeItem(RdfBaseModel):
    rdf_type: ClassVar = CDI.InstanceVariable
    rdf_preserve_unmodeled_types: ClassVar = False
    rdf_prefixes: ClassVar = {"schema": SCHEMA, "cdi": CDI, "ex": EX}

    id: str | None = None
    name: Annotated[str | None, RdfProperty(SCHEMA.name)] = None


class PropertyValueModel(RdfBaseModel):
    rdf_type: ClassVar = SCHEMA.PropertyValue
    id: str | None = None
    value: Annotated[str | None, RdfProperty(SCHEMA.value)] = None


class InstanceVariableModel(RdfBaseModel):
    rdf_type: ClassVar = [SCHEMA.PropertyValue, CDI.InstanceVariable]
    id: str | None = None
    name: Annotated[str | None, RdfProperty(SCHEMA.name)] = None


class ContainerModel(RdfBaseModel):
    rdf_type: ClassVar = SCHEMA.Dataset
    id: str | None = None
    elements: Annotated[list[InstanceVariableModel | PropertyValueModel], RdfProperty(SCHEMA.hasPart)] = []


def test_multi_type_serialization_to_graph() -> None:
    """Test that a model with multiple rdf_type values emits all types as RDF.type triples."""
    item = MultiTypeItem(id="http://example.org/item1", name="Variable1")
    graph = item.to_rdf_graph()

    subject = URIRef("http://example.org/item1")
    types = list(graph.objects(subject, RDF.type))

    assert SCHEMA.PropertyValue in types
    assert CDI.InstanceVariable in types
    assert len(types) == 2
    assert (subject, SCHEMA.name, Literal("Variable1")) in graph


def test_multi_type_serialization_formats() -> None:
    """Test serializing multi-type models to Turtle and JSON-LD formats."""
    item = MultiTypeItem(id="http://example.org/item1", name="Variable1")

    # Serialize to Turtle
    turtle_output = item.to_rdf("turtle")
    assert "PropertyValue" in turtle_output
    assert "InstanceVariable" in turtle_output

    # Serialize to JSON-LD
    jsonld_output = item.to_rdf("json-ld")
    assert "PropertyValue" in jsonld_output
    assert "InstanceVariable" in jsonld_output


def test_multi_type_round_trip() -> None:
    """Test round-trip serialization and deserialization of a multi-typed model."""
    original = MultiTypeItem(id="http://example.org/item1", name="Variable1")
    turtle_data = original.to_rdf("turtle")

    reloaded = MultiTypeItem.from_rdf(turtle_data, format="turtle")
    assert reloaded.id == "http://example.org/item1"
    assert reloaded.name == "Variable1"

    # Verify output graph has both types
    re_graph = reloaded.to_rdf_graph()
    subject = URIRef("http://example.org/item1")
    re_types = list(re_graph.objects(subject, RDF.type))
    assert SCHEMA.PropertyValue in re_types
    assert CDI.InstanceVariable in re_types


def test_multi_type_tuple_and_set() -> None:
    """Test that tuple and set forms of rdf_type are supported."""

    class TupleTypeModel(RdfBaseModel):
        rdf_type: ClassVar = (SCHEMA.PropertyValue, CDI.InstanceVariable)
        id: str | None = None

    class SetTypeModel(RdfBaseModel):
        rdf_type: ClassVar = {SCHEMA.PropertyValue, CDI.InstanceVariable}
        id: str | None = None

    t_item = TupleTypeModel(id="http://example.org/t1")
    t_graph = t_item.to_rdf_graph()
    assert len(list(t_graph.objects(URIRef("http://example.org/t1"), RDF.type))) == 2

    s_item = SetTypeModel(id="http://example.org/s1")
    s_graph = s_item.to_rdf_graph()
    assert len(list(s_graph.objects(URIRef("http://example.org/s1"), RDF.type))) == 2


def test_multi_type_subject_inference() -> None:
    """Test that _infer_subject correctly intersects multiple types."""
    g = Graph()
    s1 = URIRef("http://example.org/var1")
    s2 = URIRef("http://example.org/pv1")

    # s1 has both types
    g.add((s1, RDF.type, SCHEMA.PropertyValue))
    g.add((s1, RDF.type, CDI.InstanceVariable))
    g.add((s1, SCHEMA.name, Literal("Var 1")))

    # s2 has only PropertyValue
    g.add((s2, RDF.type, SCHEMA.PropertyValue))
    g.add((s2, SCHEMA.name, Literal("PV 1")))

    # Inferring MultiTypeItem should match only s1 (which has both types)
    inferred = MultiTypeItem._infer_subject(g)
    assert inferred == s1
    assert inferred is not None

    loaded = MultiTypeItem.from_rdf_graph(g, inferred)
    assert loaded.id == "http://example.org/var1"
    assert loaded.name == "Var 1"


def test_multi_type_subject_inference_ambiguity_raises() -> None:
    """Test that _infer_subject raises ValueError if multiple resources match all types."""
    g = Graph()
    s1 = URIRef("http://example.org/var1")
    s2 = URIRef("http://example.org/var2")

    for s in (s1, s2):
        g.add((s, RDF.type, SCHEMA.PropertyValue))
        g.add((s, RDF.type, CDI.InstanceVariable))

    with pytest.raises(ValueError, match="Multiple resources of the requested rdf:type were found"):
        MultiTypeItem._infer_subject(g)


def test_dynamic_unmodeled_type_preservation_default() -> None:
    """Test that by default (rdf_preserve_unmodeled_types=True), extra types from the source are preserved."""
    g = Graph()
    s = URIRef("http://example.org/var1")
    g.add((s, RDF.type, CDI.InstanceVariable))
    g.add((s, RDF.type, SCHEMA.PropertyValue))  # Extra type not in SingleTypeItem
    g.add((s, RDF.type, EX.CustomTag))  # Another unmodeled type
    g.add((s, SCHEMA.name, Literal("Name1")))

    loaded = SingleTypeItem.from_rdf_graph(g, s)
    assert loaded.name == "Name1"

    out_g = loaded.to_rdf_graph()
    out_types = set(out_g.objects(s, RDF.type))

    # All three types must be preserved in the output graph
    assert CDI.InstanceVariable in out_types
    assert SCHEMA.PropertyValue in out_types
    assert EX.CustomTag in out_types


def test_dynamic_unmodeled_type_preservation_strict() -> None:
    """Test that when rdf_preserve_unmodeled_types=False, unmodeled types are stripped."""
    g = Graph()
    s = URIRef("http://example.org/var1")
    g.add((s, RDF.type, CDI.InstanceVariable))
    g.add((s, RDF.type, SCHEMA.PropertyValue))  # Extra type
    g.add((s, SCHEMA.name, Literal("Name1")))

    loaded = StrictSingleTypeItem.from_rdf_graph(g, s)
    assert loaded.name == "Name1"

    out_g = loaded.to_rdf_graph()
    out_types = set(out_g.objects(s, RDF.type))

    # Only the declared type is in the output graph
    assert out_types == {CDI.InstanceVariable}


def test_polymorphic_union_resolution() -> None:
    """Test that Union[ModelA, ModelB] fields dynamically resolve the best model based on graph types."""
    g = Graph()
    ds = URIRef("http://example.org/dataset1")
    elem_pv = URIRef("http://example.org/pv1")
    elem_iv = URIRef("http://example.org/iv1")

    g.add((ds, RDF.type, SCHEMA.Dataset))
    g.add((ds, SCHEMA.hasPart, elem_pv))
    g.add((ds, SCHEMA.hasPart, elem_iv))

    # elem_pv has only PropertyValue
    g.add((elem_pv, RDF.type, SCHEMA.PropertyValue))
    g.add((elem_pv, SCHEMA.value, Literal("Val1")))

    # elem_iv has both PropertyValue and InstanceVariable (matches InstanceVariableModel)
    g.add((elem_iv, RDF.type, SCHEMA.PropertyValue))
    g.add((elem_iv, RDF.type, CDI.InstanceVariable))
    g.add((elem_iv, SCHEMA.name, Literal("VarName1")))

    dataset = ContainerModel.from_rdf_graph(g, ds)
    assert len(dataset.elements) == 2

    # Verify that each element was deserialized to its specific matching model
    elements_by_id = {elem.id: elem for elem in dataset.elements}
    assert isinstance(elements_by_id["http://example.org/pv1"], PropertyValueModel)
    assert elements_by_id["http://example.org/pv1"].value == "Val1"

    assert isinstance(elements_by_id["http://example.org/iv1"], InstanceVariableModel)
    assert elements_by_id["http://example.org/iv1"].name == "VarName1"
