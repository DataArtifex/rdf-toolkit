"""Integration test for Cross-Domain Interoperability Framework (CDIF) SPSS pattern with multiple @type."""

import json
from typing import Annotated, ClassVar

from rdflib import RDF, Graph, Namespace, URIRef

from dartfx.rdf.pydantic import RdfBaseModel, RdfProperty

SCHEMA = Namespace("http://schema.org/")
CDI = Namespace("http://ddialliance.org/Specification/DDI-CDI/1.0/RDF/")
CDIF = Namespace("https://w3id.org/cdif/")


CDIF_SPSS_SNIPPET = {
    "@context": {
        "schema": "http://schema.org/",
        "cdi": "http://ddialliance.org/Specification/DDI-CDI/1.0/RDF/",
        "cdif": "https://w3id.org/cdif/",
    },
    "@id": "urn:ddi-cdi:wideDataSet",
    "@type": ["schema:Dataset"],
    "schema:name": "SPSS_Example",
    "schema:variableMeasured": [
        {
            "@id": "http://example.org/dataset#instanceVariable-idno",
            "@type": ["schema:PropertyValue", "cdi:InstanceVariable"],
            "schema:name": "idno",
        },
        {
            "@id": "http://example.org/dataset#instanceVariable-nwspol",
            "@type": ["schema:PropertyValue", "cdi:InstanceVariable"],
            "schema:name": "nwspol",
        },
    ],
}


class CDIFInstanceVariable(RdfBaseModel):
    """Model with static multi-type declaration matching CDIF/Schema.org/DDI-CDI."""

    rdf_type: ClassVar = [SCHEMA.PropertyValue, CDI.InstanceVariable]
    rdf_prefixes: ClassVar = {"schema": SCHEMA, "cdi": CDI, "cdif": CDIF}

    id: str | None = None
    name: Annotated[str | None, RdfProperty(SCHEMA.name)] = None


class CDIFDataset(RdfBaseModel):
    rdf_type: ClassVar = SCHEMA.Dataset
    rdf_prefixes: ClassVar = {"schema": SCHEMA, "cdi": CDI, "cdif": CDIF}

    id: str | None = None
    name: Annotated[str | None, RdfProperty(SCHEMA.name)] = None
    variables: Annotated[list[CDIFInstanceVariable], RdfProperty(SCHEMA.variableMeasured)] = []


class SingleTypeCDIFInstanceVariable(RdfBaseModel):
    """Model that only declares cdi:InstanceVariable and relies on dynamic unmodeled type preservation."""

    rdf_type: ClassVar = CDI.InstanceVariable
    rdf_prefixes: ClassVar = {"schema": SCHEMA, "cdi": CDI, "cdif": CDIF}

    id: str | None = None
    name: Annotated[str | None, RdfProperty(SCHEMA.name)] = None


class SingleTypeCDIFDataset(RdfBaseModel):
    rdf_type: ClassVar = SCHEMA.Dataset
    rdf_prefixes: ClassVar = {"schema": SCHEMA, "cdi": CDI, "cdif": CDIF}

    id: str | None = None
    variables: Annotated[list[SingleTypeCDIFInstanceVariable], RdfProperty(SCHEMA.variableMeasured)] = []


def test_cdif_spss_static_multi_type_round_trip() -> None:
    """Test deserializing and serializing CDIF SPSS snippet with static multi-type models."""
    jsonld_str = json.dumps(CDIF_SPSS_SNIPPET)

    graph = Graph()
    graph.parse(data=jsonld_str, format="json-ld")

    dataset = CDIFDataset.from_rdf_graph(graph, URIRef("urn:ddi-cdi:wideDataSet"))
    assert dataset.name == "SPSS_Example"
    assert len(dataset.variables) == 2
    assert dataset.variables[0].name == "idno"
    assert dataset.variables[1].name == "nwspol"

    # Serialize to graph
    out_graph = dataset.to_rdf_graph()

    # Verify both types exist for both variables
    for var in dataset.variables:
        var_uri = URIRef(str(var.id))
        types = set(out_graph.objects(var_uri, RDF.type))
        assert SCHEMA.PropertyValue in types
        assert CDI.InstanceVariable in types

    # Verify JSON-LD serialization round-trip
    out_jsonld = dataset.to_rdf("json-ld")
    re_parsed_graph = Graph()
    re_parsed_graph.parse(data=out_jsonld, format="json-ld")

    for var in dataset.variables:
        var_uri = URIRef(str(var.id))
        types = set(re_parsed_graph.objects(var_uri, RDF.type))
        assert SCHEMA.PropertyValue in types
        assert CDI.InstanceVariable in types


def test_cdif_spss_dynamic_type_preservation() -> None:
    """Test dynamic unmodeled type preservation.

    Keeps schema:PropertyValue even if model only declares cdi:InstanceVariable.
    """
    jsonld_str = json.dumps(CDIF_SPSS_SNIPPET)

    graph = Graph()
    graph.parse(data=jsonld_str, format="json-ld")

    dataset = SingleTypeCDIFDataset.from_rdf_graph(graph, URIRef("urn:ddi-cdi:wideDataSet"))
    assert len(dataset.variables) == 2

    # Serialize back out
    out_graph = dataset.to_rdf_graph()

    for var in dataset.variables:
        var_uri = URIRef(str(var.id))
        types = set(out_graph.objects(var_uri, RDF.type))
        # Both types must be present because schema:PropertyValue was preserved from source graph
        assert SCHEMA.PropertyValue in types
        assert CDI.InstanceVariable in types
