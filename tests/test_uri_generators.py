"""Tests for RdfUriGenerator Protocol, DefaultUriGenerator, and all additional generators."""

from __future__ import annotations

import re
from typing import Annotated, ClassVar

from rdflib import BNode, Namespace, URIRef

from dartfx.rdf.pydantic import (
    CompositeUriGenerator,
    DefaultUriGenerator,
    HashUriGenerator,
    PrefixedUriGenerator,
    RdfBaseModel,
    RdfProperty,
    RdfUriGenerator,
    TemplateUriGenerator,
)

EX = Namespace("https://example.org/")
EX_PERSON = Namespace("https://example.org/person/")


# ---------------------------------------------------------------------------
# Shared fixture models
# ---------------------------------------------------------------------------


class Person(RdfBaseModel):
    rdf_type: ClassVar = EX.Person
    rdf_namespace: ClassVar = EX_PERSON

    id: str | None = None
    name: Annotated[str | None, RdfProperty(EX.name)] = None


class NoNsPerson(RdfBaseModel):
    """A model without a namespace, to test base_uri and raw-URI fallbacks."""

    rdf_type: ClassVar = EX.Person

    id: str | None = None
    name: Annotated[str | None, RdfProperty(EX.name)] = None


class Article(RdfBaseModel):
    rdf_type: ClassVar = EX.Article
    rdf_namespace: ClassVar = EX

    id: str | None = None
    title: Annotated[str | None, RdfProperty(EX.title)] = None
    year: Annotated[int | None, RdfProperty(EX.year)] = None


# ---------------------------------------------------------------------------
# DefaultUriGenerator — unit-level tests
# ---------------------------------------------------------------------------


def test_default_generator_with_id() -> None:
    """With an id set, DefaultUriGenerator produces namespace + id."""
    gen = DefaultUriGenerator()
    person = Person(id="alice", name="Alice")
    assert gen(person) == URIRef(str(EX_PERSON) + "alice")


def test_default_generator_full_uri_id() -> None:
    """If id already looks like a URI, it is used as-is."""
    gen = DefaultUriGenerator()
    person = Person(id="https://example.org/people/alice")
    assert gen(person) == URIRef("https://example.org/people/alice")


def test_default_generator_base_uri() -> None:
    """base_uri is respected when no namespace is defined on the model."""
    gen = DefaultUriGenerator()
    person = NoNsPerson(id="bob")
    assert gen(person, base_uri="https://example.org/people/") == URIRef("https://example.org/people/bob")


def test_default_generator_auto_uuid_true() -> None:
    """No id + auto_uuid=True → a UUID-based URI is minted."""
    gen = DefaultUriGenerator(auto_uuid=True)
    person = Person(name="Alice")
    uri = gen(person)
    assert isinstance(uri, URIRef)
    assert str(uri).startswith(str(EX_PERSON))


def test_default_generator_auto_uuid_false() -> None:
    """No id + auto_uuid=False → BNode."""
    gen = DefaultUriGenerator(auto_uuid=False)
    assert isinstance(gen(Person(name="Alice")), BNode)


def test_default_generator_auto_uuid_false_id_still_works() -> None:
    """auto_uuid=False does NOT suppress URI generation when an id is present."""
    gen = DefaultUriGenerator(auto_uuid=False)
    assert gen(Person(id="charlie")) == URIRef(str(EX_PERSON) + "charlie")


# ---------------------------------------------------------------------------
# Instance-level generator — newly unlocked behaviour
# ---------------------------------------------------------------------------


def test_instance_level_generator_overrides_id() -> None:
    """A custom generator on the instance overrides the default *even* when id is set.

    Previously the id-field check was hardcoded before the generator was consulted.
    """

    def my_gen(model: RdfBaseModel, *, base_uri: str | None = None) -> URIRef | BNode:  # noqa: ARG001
        return EX[f"custom/{type(model).__name__}"]

    person = Person(id="alice", name="Alice", rdf_uri_generator=my_gen)
    subjects = set(person.to_rdf_graph().subjects())
    assert len(subjects) == 1
    assert next(iter(subjects)) == EX["custom/Person"]


# ---------------------------------------------------------------------------
# Call-site generator overrides instance generator
# ---------------------------------------------------------------------------


def test_call_site_generator_overrides_instance() -> None:
    """Generator passed to to_rdf_graph() takes priority over the instance generator."""

    def instance_gen(model: RdfBaseModel, *, base_uri: str | None = None) -> URIRef | BNode:  # noqa: ARG001
        return EX["instance"]

    def call_site_gen(model: RdfBaseModel, *, base_uri: str | None = None) -> URIRef | BNode:  # noqa: ARG001
        return EX["callsite"]

    person = Person(id="alice", rdf_uri_generator=instance_gen)
    subjects = set(person.to_rdf_graph(rdf_uri_generator=call_site_gen).subjects())
    assert next(iter(subjects)) == EX["callsite"]


# ---------------------------------------------------------------------------
# Protocol compliance
# ---------------------------------------------------------------------------


def test_plain_function_satisfies_protocol() -> None:
    """A plain function with the correct signature satisfies RdfUriGenerator."""

    def my_gen(model: RdfBaseModel, *, base_uri: str | None = None) -> URIRef | BNode:  # noqa: ARG001
        return EX["x"]

    assert isinstance(my_gen, RdfUriGenerator)


def test_all_generators_satisfy_protocol() -> None:
    """All provided generator classes satisfy RdfUriGenerator."""
    assert isinstance(DefaultUriGenerator(), RdfUriGenerator)
    assert isinstance(TemplateUriGenerator("https://example.org/{id}"), RdfUriGenerator)
    assert isinstance(HashUriGenerator(namespace="https://example.org/", fields=["id"]), RdfUriGenerator)
    assert isinstance(CompositeUriGenerator(DefaultUriGenerator()), RdfUriGenerator)
    assert isinstance(PrefixedUriGenerator(prefix="https://example.org/", field="id"), RdfUriGenerator)


# ---------------------------------------------------------------------------
# Removed field
# ---------------------------------------------------------------------------


def test_rdf_auto_uuid_not_a_model_field() -> None:
    """rdf_auto_uuid is no longer a model field; use DefaultUriGenerator(auto_uuid=False)."""
    assert not hasattr(Person(), "rdf_auto_uuid")


# ---------------------------------------------------------------------------
# BNode end-to-end
# ---------------------------------------------------------------------------


def test_bnode_produced_when_auto_uuid_false() -> None:
    """DefaultUriGenerator(auto_uuid=False) produces a BNode subject."""
    person = Person(name="Dave", rdf_uri_generator=DefaultUriGenerator(auto_uuid=False))
    subjects = set(person.to_rdf_graph().subjects())
    assert len(subjects) == 1
    assert isinstance(next(iter(subjects)), BNode)


# ---------------------------------------------------------------------------
# TemplateUriGenerator
# ---------------------------------------------------------------------------


def test_template_basic() -> None:
    gen = TemplateUriGenerator("https://example.org/articles/{year}/{id}")
    article = Article(id="climate", year=2024, title="Climate Data")
    assert gen(article) == URIRef("https://example.org/articles/2024/climate")


def test_template_missing_field_returns_bnode() -> None:
    """If a placeholder field is None, fall back to BNode."""
    gen = TemplateUriGenerator("https://example.org/articles/{year}/{id}")
    assert isinstance(gen(Article(id="no-year")), BNode)  # year is None


def test_template_via_model() -> None:
    """Set TemplateUriGenerator at the instance level and serialise."""
    article = Article(
        id="ai-survey",
        year=2025,
        title="AI Survey",
        rdf_uri_generator=TemplateUriGenerator("https://example.org/a/{year}/{id}"),
    )
    subjects = set(article.to_rdf_graph().subjects())
    assert URIRef("https://example.org/a/2025/ai-survey") in subjects


# ---------------------------------------------------------------------------
# HashUriGenerator
# ---------------------------------------------------------------------------


def test_hash_produces_uri() -> None:
    gen = HashUriGenerator(namespace="https://example.org/h/", fields=["title"])
    result = gen(Article(title="Hello World"))
    assert isinstance(result, URIRef)
    assert re.match(r"https://example\.org/h/[0-9a-f]{64}$", str(result))


def test_hash_is_deterministic() -> None:
    """Same input always produces the same URI."""
    gen = HashUriGenerator(namespace="https://example.org/h/", fields=["title", "year"])
    assert gen(Article(title="Foo", year=2024)) == gen(Article(title="Foo", year=2024))


def test_hash_different_content_different_uri() -> None:
    gen = HashUriGenerator(namespace="https://example.org/h/", fields=["title"])
    assert gen(Article(title="Foo")) != gen(Article(title="Bar"))


def test_hash_no_fields_returns_bnode() -> None:
    """All specified fields are None → BNode."""
    gen = HashUriGenerator(namespace="https://example.org/h/", fields=["title"])
    assert isinstance(gen(Article()), BNode)


def test_hash_algorithm_sha1() -> None:
    gen = HashUriGenerator(namespace="https://example.org/h/", fields=["title"], algorithm="sha1")
    assert re.match(r"https://example\.org/h/[0-9a-f]{40}$", str(gen(Article(title="Test"))))


def test_hash_namespace_trailing_slash_normalised() -> None:
    """Trailing slash is normalised — don't double up."""
    a = Article(title="Same")
    gen1 = HashUriGenerator(namespace="https://example.org/h/", fields=["title"])
    gen2 = HashUriGenerator(namespace="https://example.org/h", fields=["title"])
    assert gen1(a) == gen2(a)


# ---------------------------------------------------------------------------
# CompositeUriGenerator
# ---------------------------------------------------------------------------


def test_composite_uses_first_uri_result() -> None:
    """Returns the first non-BNode result."""
    gen = CompositeUriGenerator(
        DefaultUriGenerator(auto_uuid=False),
        HashUriGenerator(namespace="https://example.org/h/", fields=["title"]),
    )
    result = gen(Article(title="Fallback Article"))  # no id → first returns BNode
    assert isinstance(result, URIRef)
    assert str(result).startswith("https://example.org/h/")


def test_composite_first_wins() -> None:
    """If the first generator returns a URIRef, the second is not used."""
    gen = CompositeUriGenerator(
        DefaultUriGenerator(auto_uuid=False),
        HashUriGenerator(namespace="https://example.org/h/", fields=["title"]),
    )
    assert gen(Article(id="explicit-id", title="My Article")) == URIRef(str(EX) + "explicit-id")


def test_composite_all_fail_returns_bnode() -> None:
    """If every generator returns a BNode, the composite also returns BNode."""
    gen = CompositeUriGenerator(
        DefaultUriGenerator(auto_uuid=False),
        HashUriGenerator(namespace="https://example.org/h/", fields=["title"]),
    )
    assert isinstance(gen(Article()), BNode)  # no id, no title


def test_composite_strategy_end_to_end() -> None:
    """Full serialisation test using CompositeUriGenerator via instance field."""
    gen = CompositeUriGenerator(
        DefaultUriGenerator(auto_uuid=False),
        HashUriGenerator(namespace="https://example.org/articles/", fields=["title"]),
    )
    article = Article(title="Deep Learning", rdf_uri_generator=gen)
    subjects = set(article.to_rdf_graph().subjects())
    assert len(subjects) == 1
    subject = next(iter(subjects))
    assert isinstance(subject, URIRef)
    assert str(subject).startswith("https://example.org/articles/")


# ---------------------------------------------------------------------------
# PrefixedUriGenerator
# ---------------------------------------------------------------------------


def test_prefixed_basic() -> None:
    gen = PrefixedUriGenerator(prefix="https://vocab.example.org/c/", field="id")
    assert gen(Article(id="001")) == URIRef("https://vocab.example.org/c/001")


def test_prefixed_none_field_returns_bnode() -> None:
    gen = PrefixedUriGenerator(prefix="https://vocab.example.org/c/", field="id")
    assert isinstance(gen(Article()), BNode)


def test_prefixed_trailing_slash_normalised() -> None:
    article = Article(id="abc")
    gen1 = PrefixedUriGenerator(prefix="https://vocab.example.org/c/", field="id")
    gen2 = PrefixedUriGenerator(prefix="https://vocab.example.org/c", field="id")
    assert gen1(article) == gen2(article)


def test_prefixed_non_id_field() -> None:
    """Can prefix any field, not just id."""
    gen = PrefixedUriGenerator(prefix="https://example.org/title/", field="title")
    assert gen(Article(title="hello")) == URIRef("https://example.org/title/hello")
