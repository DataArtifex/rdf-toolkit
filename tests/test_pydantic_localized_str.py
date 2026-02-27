from typing import Annotated

import pytest
from rdflib import SKOS, Graph, Literal, Namespace

from dartfx.rdf.pydantic import LangString, LocalizedStr, RdfBaseModel, RdfProperty

EX = Namespace("http://example.org/")


class LocalizedModel(RdfBaseModel):
    rdf_type = EX.LocalizedResource
    rdf_namespace = EX

    id: str
    label: Annotated[LocalizedStr | None, RdfProperty(SKOS.prefLabel)] = None
    note: Annotated[LocalizedStr | None, RdfProperty(SKOS.note)] = None


def test_localized_str_plain_string():
    """Test with a simple plain string."""
    m = LocalizedModel(id="1", label="Plain")
    g = m.to_rdf_graph()

    # Verify RDF
    labels = list(g.objects(EX["1"], SKOS.prefLabel))
    assert len(labels) == 1
    assert str(labels[0]) == "Plain"
    assert labels[0].language is None

    # Round-trip
    restored = LocalizedModel.from_rdf_graph(g, subject=EX["1"])
    assert restored.label == "Plain"


def test_localized_str_lang_string_object():
    """Test with an explicit LangString object."""
    m = LocalizedModel(id="2", label=LangString(value="Hello", lang="en"))
    g = m.to_rdf_graph()

    # Verify RDF
    labels = list(g.objects(EX["2"], SKOS.prefLabel))
    assert len(labels) == 1
    assert str(labels[0]) == "Hello"
    assert labels[0].language == "en"

    # Round-trip (Deserializes to dict when tags are present)
    restored = LocalizedModel.from_rdf_graph(g, subject=EX["2"])
    assert restored.label == {"en": "Hello"}


def test_localized_str_dict_mapping():
    """Test with a language map dictionary."""
    m = LocalizedModel(id="3", label={"en": "World", "es": "Mundo"})
    g = m.to_rdf_graph()

    # Verify RDF
    labels = list(g.objects(EX["3"], SKOS.prefLabel))
    assert len(labels) == 2

    # Check that we have both expected literals
    found_en = any(str(lit) == "World" and lit.language == "en" for lit in labels)
    found_es = any(str(lit) == "Mundo" and lit.language == "es" for lit in labels)
    assert found_en
    assert found_es

    # Round-trip
    restored = LocalizedModel.from_rdf_graph(g, subject=EX["3"])
    assert restored.label == {"en": "World", "es": "Mundo"}


def test_localized_str_dict_with_lists():
    """Test with a language map containing multiple values per tag."""
    m = LocalizedModel(id="4", label={"en": ["Earth", "World"], "fr": "Monde"})
    g = m.to_rdf_graph()

    # Verify RDF
    labels = list(g.objects(EX["4"], SKOS.prefLabel))
    assert len(labels) == 3

    # Round-trip
    restored = LocalizedModel.from_rdf_graph(g, subject=EX["4"])
    assert isinstance(restored.label, dict)
    assert set(restored.label["en"]) == {"Earth", "World"}
    assert restored.label["fr"] == "Monde"


def test_localized_str_list_of_mixed():
    """Test with a list containing mixed types (str, LangString)."""
    m = LocalizedModel(
        id="5",
        label=["Plain", LangString(value="Hello", lang="en"), "Another Plain", LangString(value="Bonjour", lang="fr")],
    )
    g = m.to_rdf_graph()

    # Verify RDF
    labels = list(g.objects(EX["5"], SKOS.prefLabel))
    assert len(labels) == 4

    # Round-trip (Expect aggregation into dict because language tags are mixed with plain)
    # Note: plain strings get "" key in dict aggregation
    restored = LocalizedModel.from_rdf_graph(g, subject=EX["5"])
    assert isinstance(restored.label, dict)
    assert set(restored.label[""]) == {"Plain", "Another Plain"}
    assert restored.label["en"] == "Hello"
    assert restored.label["fr"] == "Bonjour"


def test_localized_str_none():
    """Test with None value."""
    m = LocalizedModel(id="6", label=None)
    g = m.to_rdf_graph()

    # Verify RDF (no triples should be emitted for label)
    assert len(list(g.triples((EX["6"], SKOS.prefLabel, None)))) == 0

    # Round-trip
    restored = LocalizedModel.from_rdf_graph(g, subject=EX["6"])
    assert restored.label is None


def test_localized_str_empty_list_and_dict():
    """Test with empty structures."""
    m1 = LocalizedModel(id="7a", label=[])
    m2 = LocalizedModel(id="7b", label={})

    g1 = m1.to_rdf_graph()
    g2 = m2.to_rdf_graph()

    assert len(list(g1.triples((EX["7a"], SKOS.prefLabel, None)))) == 0
    assert len(list(g2.triples((EX["7b"], SKOS.prefLabel, None)))) == 0


def test_localized_str_multiple_tags_deserialization():
    """Verify that multiple tags correctly aggregate even without explicit model initialization."""
    g = Graph()
    subj = EX["custom"]
    g.add((subj, SKOS.prefLabel, Literal("Hello", lang="en")))
    g.add((subj, SKOS.prefLabel, Literal("Hi", lang="en")))
    g.add((subj, SKOS.prefLabel, Literal("Mundo", lang="es")))

    m = LocalizedModel.from_rdf_graph(g, subject=subj)
    assert isinstance(m.label, dict)
    assert set(m.label["en"]) == {"Hello", "Hi"}
    assert m.label["es"] == "Mundo"


def test_lang_string_behavior():
    """Verify string-like behavior for LangString."""
    ls = LangString(value="Hello", lang="en")

    # String conversion
    assert str(ls) == "Hello"

    # Representation (RDF style)
    assert repr(ls) == '"Hello"@en'
    assert repr(LangString(value="Hello")) == '"Hello"'

    # Equality with strings (removed, check value directly)
    assert ls.value == "Hello"
    assert ls != "Hello"  # Because they are different types now
    assert ls != "World"

    # Equality with other LangStrings
    assert ls == LangString(value="Hello", lang="en")
    assert ls != LangString(value="Hello", lang="fr")
    assert ls != LangString(value="World", lang="en")

    # Hashability (for sets/dict keys)
    s = {ls, "Hello"}
    assert len(s) == 2  # They are different types but can coexist in a set
    assert LangString(value="Hello", lang="en") in s


if __name__ == "__main__":
    pytest.main([__file__])
