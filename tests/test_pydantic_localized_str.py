from typing import Annotated

import pytest
from rdflib import SKOS, Graph, Literal, Namespace

from dartfx.rdf.pydantic import LangString, LangStringList, LocalizedStr, RdfBaseModel, RdfProperty

EX = Namespace("http://example.org/")


class LocalizedModel(RdfBaseModel):
    rdf_type = EX.LocalizedResource
    rdf_namespace = EX

    id: str
    label: Annotated[LocalizedStr | None, RdfProperty(SKOS.prefLabel)] = None
    note: Annotated[LocalizedStr | None, RdfProperty(SKOS.note)] = None


def _label_list(model: LocalizedModel) -> LangStringList:
    assert isinstance(model.label, LangStringList)
    return model.label


# ---------------------------------------------------------------------------
# Coercion tests – verify flexible input → canonical list[LangString]
# ---------------------------------------------------------------------------


def test_coerce_plain_string():
    """A plain string is coerced to [LangString(value=..., lang=None)]."""
    m = LocalizedModel(id="1", label="Plain")
    assert _label_list(m) == [LangString(value="Plain", lang=None)]


def test_coerce_lang_string_object():
    """A single LangString is wrapped in a list."""
    m = LocalizedModel(id="2", label=LangString(value="Hello", lang="en"))
    assert _label_list(m) == [LangString(value="Hello", lang="en")]


def test_coerce_dict_mapping():
    """A language-map dict is expanded into a list of LangString."""
    m = LocalizedModel(id="3", label={"en": "World", "es": "Mundo"})
    assert set(_label_list(m)) == {
        LangString(value="World", lang="en"),
        LangString(value="Mundo", lang="es"),
    }


def test_coerce_dict_with_lists():
    """Dict values that are lists expand into multiple LangString entries."""
    m = LocalizedModel(id="4", label={"en": ["Earth", "World"], "fr": "Monde"})
    assert set(_label_list(m)) == {
        LangString(value="Earth", lang="en"),
        LangString(value="World", lang="en"),
        LangString(value="Monde", lang="fr"),
    }


def test_coerce_list_of_mixed():
    """A list of mixed str/LangString is flattened into list[LangString]."""
    m = LocalizedModel(
        id="5",
        label=["Plain", LangString(value="Hello", lang="en"), "Another Plain", LangString(value="Bonjour", lang="fr")],
    )
    assert _label_list(m) == [
        LangString(value="Plain", lang=None),
        LangString(value="Hello", lang="en"),
        LangString(value="Another Plain", lang=None),
        LangString(value="Bonjour", lang="fr"),
    ]


# ---------------------------------------------------------------------------
# Uniqueness tests
# ---------------------------------------------------------------------------


def test_uniqueness_dedup():
    """Duplicate (value, lang) pairs are silently dropped."""
    m = LocalizedModel(
        id="u1",
        label=[
            LangString(value="Hello", lang="en"),
            LangString(value="Hello", lang="en"),
            LangString(value="Hello", lang="fr"),
        ],
    )
    assert _label_list(m) == [
        LangString(value="Hello", lang="en"),
        LangString(value="Hello", lang="fr"),
    ]


def test_uniqueness_dict_dedup():
    """Duplicate values within a dict are deduplicated."""
    m = LocalizedModel(id="u2", label={"en": ["World", "World"]})
    assert _label_list(m) == [LangString(value="World", lang="en")]


# ---------------------------------------------------------------------------
# RDF serialization round-trip tests
# ---------------------------------------------------------------------------


def test_localized_str_plain_string_roundtrip():
    """Plain string round-trips through RDF."""
    m = LocalizedModel(id="1", label="Plain")
    g = m.to_rdf_graph()

    # Verify RDF
    labels = [lit for lit in g.objects(EX["1"], SKOS.prefLabel) if isinstance(lit, Literal)]
    assert len(labels) == 1
    assert str(labels[0]) == "Plain"
    assert labels[0].language is None

    # Round-trip
    restored = LocalizedModel.from_rdf_graph(g, subject=EX["1"])
    assert _label_list(restored) == [LangString(value="Plain", lang=None)]


def test_localized_str_lang_string_object_roundtrip():
    """Explicit LangString round-trips through RDF."""
    m = LocalizedModel(id="2", label=LangString(value="Hello", lang="en"))
    g = m.to_rdf_graph()

    # Verify RDF
    labels = [lit for lit in g.objects(EX["2"], SKOS.prefLabel) if isinstance(lit, Literal)]
    assert len(labels) == 1
    assert str(labels[0]) == "Hello"
    assert labels[0].language == "en"

    # Round-trip
    restored = LocalizedModel.from_rdf_graph(g, subject=EX["2"])
    assert _label_list(restored) == [LangString(value="Hello", lang="en")]


def test_localized_str_dict_mapping_roundtrip():
    """Language-map dict round-trips through RDF."""
    m = LocalizedModel(id="3", label={"en": "World", "es": "Mundo"})
    g = m.to_rdf_graph()

    # Verify RDF
    labels = [lit for lit in g.objects(EX["3"], SKOS.prefLabel) if isinstance(lit, Literal)]
    assert len(labels) == 2

    found_en = any(str(lit) == "World" and lit.language == "en" for lit in labels)
    found_es = any(str(lit) == "Mundo" and lit.language == "es" for lit in labels)
    assert found_en
    assert found_es

    # Round-trip
    restored = LocalizedModel.from_rdf_graph(g, subject=EX["3"])
    assert set(_label_list(restored)) == {
        LangString(value="World", lang="en"),
        LangString(value="Mundo", lang="es"),
    }


def test_localized_str_dict_with_lists_roundtrip():
    """Dict with list values round-trips through RDF."""
    m = LocalizedModel(id="4", label={"en": ["Earth", "World"], "fr": "Monde"})
    g = m.to_rdf_graph()

    # Verify RDF
    labels = list(g.objects(EX["4"], SKOS.prefLabel))
    assert len(labels) == 3

    # Round-trip
    restored = LocalizedModel.from_rdf_graph(g, subject=EX["4"])
    assert set(_label_list(restored)) == {
        LangString(value="Earth", lang="en"),
        LangString(value="World", lang="en"),
        LangString(value="Monde", lang="fr"),
    }


def test_localized_str_list_of_mixed_roundtrip():
    """List of mixed str/LangString round-trips through RDF."""
    m = LocalizedModel(
        id="5",
        label=["Plain", LangString(value="Hello", lang="en"), "Another Plain", LangString(value="Bonjour", lang="fr")],
    )
    g = m.to_rdf_graph()

    # Verify RDF
    labels = list(g.objects(EX["5"], SKOS.prefLabel))
    assert len(labels) == 4

    # Round-trip
    restored = LocalizedModel.from_rdf_graph(g, subject=EX["5"])
    assert set(_label_list(restored)) == {
        LangString(value="Plain", lang=None),
        LangString(value="Hello", lang="en"),
        LangString(value="Another Plain", lang=None),
        LangString(value="Bonjour", lang="fr"),
    }


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
    """Verify that multiple tags correctly produce list[LangString]."""
    g = Graph()
    subj = EX["custom"]
    g.add((subj, SKOS.prefLabel, Literal("Hello", lang="en")))
    g.add((subj, SKOS.prefLabel, Literal("Hi", lang="en")))
    g.add((subj, SKOS.prefLabel, Literal("Mundo", lang="es")))

    m = LocalizedModel.from_rdf_graph(g, subject=subj)
    assert isinstance(m.label, list)
    assert set(_label_list(m)) == {
        LangString(value="Hello", lang="en"),
        LangString(value="Hi", lang="en"),
        LangString(value="Mundo", lang="es"),
    }


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


# ---------------------------------------------------------------------------
# List mutation tests
# ---------------------------------------------------------------------------


def test_list_append():
    """LangString items can be appended to a LocalizedStr field."""
    m = LocalizedModel(id="mut1", label="Initial")
    label = _label_list(m)
    label.append(LangString(value="Extra", lang="de"))
    assert LangString(value="Extra", lang="de") in label
    assert len(label) == 2


def test_list_iadd():
    """list += works for adding LangString items."""
    m = LocalizedModel(id="mut2", label="Initial")
    label = _label_list(m)
    label += [LangString(value="Extra", lang="de")]
    assert LangString(value="Extra", lang="de") in label


def test_iadd_single_langstring():
    """list += works with a single LangString (not wrapped in a list)."""
    m = LocalizedModel(id="mut3", label="Initial")
    label = _label_list(m)
    label += LangString(value="Neu", lang="de")
    assert LangString(value="Neu", lang="de") in label
    assert len(label) == 2


def test_append_dedup():
    """Appending a duplicate (value, lang) pair is silently ignored."""
    m = LocalizedModel(id="mut4", label="Initial")
    label = _label_list(m)
    label.append(LangString(value="Initial", lang=None))  # already exists
    assert len(label) == 1


# ---------------------------------------------------------------------------
# LangStringList query method tests
# ---------------------------------------------------------------------------


def test_count_by_lang():
    """count_by_lang returns the number of entries for a given language."""
    m = LocalizedModel(
        id="q1",
        label=[
            LangString(value="Hello", lang="en"),
            LangString(value="Hi", lang="en"),
            LangString(value="Bonjour", lang="fr"),
        ],
    )
    label = _label_list(m)
    assert label.count_by_lang("en") == 2
    assert label.count_by_lang("fr") == 1
    assert label.count_by_lang("de") == 0
    assert label.count_by_lang(None) == 0


def test_has_language():
    """has_language returns True if the language tag is present."""
    m = LocalizedModel(
        id="q2",
        label={"en": "Hello", "fr": "Bonjour"},
    )
    label = _label_list(m)
    assert label.has_language("en") is True
    assert label.has_language("fr") is True
    assert label.has_language("de") is False


def test_has_synonyms():
    """has_synonyms returns True if a language has more than one entry."""
    m = LocalizedModel(
        id="q3",
        label=[
            LangString(value="Hello", lang="en"),
            LangString(value="Hi", lang="en"),
            LangString(value="Bonjour", lang="fr"),
        ],
    )
    label = _label_list(m)
    assert label.has_synonyms("en") is True
    assert label.has_synonyms("fr") is False


def test_languages():
    """languages returns the set of distinct language tags."""
    m = LocalizedModel(
        id="q4",
        label=[
            "Plain",
            LangString(value="Hello", lang="en"),
            LangString(value="Bonjour", lang="fr"),
        ],
    )
    assert _label_list(m).languages() == {None, "en", "fr"}


def test_has_untagged():
    """has_untagged returns True when untagged entries exist."""
    m1 = LocalizedModel(id="hnl1", label="Plain")
    assert _label_list(m1).has_untagged() is True

    m2 = LocalizedModel(id="hnl2", label=LangString(value="Hello", lang="en"))
    assert _label_list(m2).has_untagged() is False


def test_has_language_none():
    """has_language(None) works the same as has_no_language."""
    m = LocalizedModel(id="hln1", label="Plain")
    label = _label_list(m)
    assert label.has_language(None) is True
    assert label.has_language("en") is False


def test_count_by_lang_empty_string():
    """count_by_lang('') normalizes to count_by_lang(None)."""
    m = LocalizedModel(id="cbl1", label=["Plain", "Another plain"])
    label = _label_list(m)
    assert label.count_by_lang("") == 2
    assert label.count_by_lang(None) == 2


def test_untagged():
    """untagged() returns only the language-agnostic entries."""
    m = LocalizedModel(
        id="ut1",
        label=["Plain", LangString(value="Hello", lang="en"), "Also plain"],
    )
    result = _label_list(m).untagged()
    assert len(result) == 2
    assert all(ls.lang is None for ls in result)


def test_get_by_language():
    """get_by_language returns entries for a specific language."""
    m = LocalizedModel(
        id="gbl1",
        label=[
            LangString(value="Hello", lang="en"),
            LangString(value="Hi", lang="en"),
            LangString(value="Bonjour", lang="fr"),
            "Plain",
        ],
    )
    label = _label_list(m)
    en = label.get_by_language("en")
    assert len(en) == 2
    assert all(ls.lang == "en" for ls in en)

    fr = label.get_by_language("fr")
    assert len(fr) == 1

    untagged = label.get_by_language(None)
    assert len(untagged) == 1

    # "" normalizes to None
    assert label.get_by_language("") == untagged


# ---------------------------------------------------------------------------
# Subtraction tests
# ---------------------------------------------------------------------------


def test_isub_single():
    """-= removes a matching LangString entry."""
    m = LocalizedModel(
        id="sub1",
        label=[
            LangString(value="Hello", lang="en"),
            LangString(value="Bonjour", lang="fr"),
        ],
    )
    label = _label_list(m)
    label -= LangString(value="Hello", lang="en")
    assert len(label) == 1
    assert label == [LangString(value="Bonjour", lang="fr")]


def test_sub_returns_new():
    """- returns a new LangStringList without the removed entry."""
    m = LocalizedModel(
        id="sub2",
        label=[
            LangString(value="Hello", lang="en"),
            LangString(value="Bonjour", lang="fr"),
        ],
    )
    label = _label_list(m)
    result = label - LangString(value="Hello", lang="en")
    assert len(result) == 1
    assert len(label) == 2  # original unchanged


def test_isub_no_match():
    """-= with non-matching entry leaves list unchanged."""
    m = LocalizedModel(id="sub3", label="Hello")
    label = _label_list(m)
    label -= LangString(value="World", lang="en")
    assert len(label) == 1


# ---------------------------------------------------------------------------
# Str-like behaviour tests
# ---------------------------------------------------------------------------


def test_str_single_entry():
    """str() returns the value when there is exactly one entry."""
    m = LocalizedModel(id="str1", label="Hello")
    assert str(m.label) == "Hello"


def test_str_single_untagged_among_tagged():
    """str() returns the untagged value when it's the only untagged entry."""
    m = LocalizedModel(
        id="str2",
        label=[
            "Plain text",
            LangString(value="Hello", lang="en"),
            LangString(value="Bonjour", lang="fr"),
        ],
    )
    assert str(m.label) == "Plain text"


def test_eq_single_entry_str():
    """== with str works when there is exactly one entry."""
    m = LocalizedModel(id="eq1", label="Hello")
    assert m.label == "Hello"
    assert m.label != "World"


def test_eq_single_untagged_among_tagged():
    """== with str works when there is one untagged entry among tagged."""
    m = LocalizedModel(
        id="eq2",
        label=[
            "Plain text",
            LangString(value="Hello", lang="en"),
        ],
    )
    assert m.label == "Plain text"
    assert m.label != "Hello"  # "Hello" is tagged, not the untagged value


def test_eq_multiple_untagged_no_str_match():
    """== with str returns False when there are multiple untagged entries."""
    m = LocalizedModel(id="eq3", label=["One", "Two"])
    assert m.label != "One"
    assert m.label != "Two"


def test_eq_list_comparison():
    """== with list[LangString] still works normally."""
    m = LocalizedModel(id="eq4", label="Hello")
    assert m.label == [LangString(value="Hello", lang=None)]


if __name__ == "__main__":
    pytest.main([__file__])
