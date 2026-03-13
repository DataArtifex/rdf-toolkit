"""Additional RDF subject URI generators for :mod:`dartfx.rdf.pydantic`.

This module provides a collection of ready-to-use :class:`RdfUriGenerator`
implementations beyond the :class:`~dartfx.rdf.pydantic.DefaultUriGenerator`
that is built into :class:`~dartfx.rdf.pydantic.RdfBaseModel`.

Available generators:

* :class:`TemplateUriGenerator`
* :class:`HashUriGenerator`
* :class:`CompositeUriGenerator`
* :class:`PrefixedUriGenerator`

Choosing the right generator
-----------------------------

* **No explicit identifier** available, and the resource has **global identity**
  → use :class:`DefaultUriGenerator` (UUID on) or :class:`HashUriGenerator`.

* **No explicit identifier** available, and the resource is **local / anonymous**
  (e.g. a reified statement, an intermediate blank node in a graph pattern)
  → use :class:`DefaultUriGenerator` with ``auto_uuid=False``, which returns a
  :class:`~rdflib.BNode`.  This is more semantically correct per the RDF
  specification, but BNodes cannot be referenced across graph boundaries.

* **Identifier is embedded in existing fields** and you want to build a
  structured URI without changing the model
  → use :class:`TemplateUriGenerator` or :class:`PrefixedUriGenerator`.

* **No stable identifier exists** but you need a **deterministic, reproducible**
  URI from the model's content (useful for deduplication)
  → use :class:`HashUriGenerator`.

* **Multiple strategies** needed with a clear priority order
  → wrap them in :class:`CompositeUriGenerator`.
"""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING, Any

from rdflib import BNode, Namespace, URIRef

if TYPE_CHECKING:
    from dartfx.rdf.pydantic._base import RdfBaseModel, RdfUriGenerator


class TemplateUriGenerator:
    """URI generator driven by a Python format-string template.

    Placeholders are replaced with model field values using
    :meth:`str.format_map`.  If a placeholder refers to a field that is
    ``None`` or absent, the generator returns a :class:`~rdflib.BNode` rather
    than producing a malformed URI.

    Parameters
    ----------
    template : str
        A URI string with ``{field_name}`` placeholders.  Any field accessible
        via :meth:`~pydantic.BaseModel.model_dump` can be referenced.

    Examples
    --------
    ::

        from dartfx.rdf.pydantic import RdfBaseModel, RdfProperty
        from dartfx.rdf.pydantic._uri_generators import TemplateUriGenerator
        from rdflib import Namespace

        EX = Namespace("https://example.org/")

        class Dataset(RdfBaseModel):
            rdf_namespace = EX
            rdf_uri_generator = TemplateUriGenerator(
                "https://example.org/datasets/{year}/{slug}"
            )

            year: int | None = None
            slug: str | None = None

        ds = Dataset(year=2024, slug="climate-data")
        ttl = ds.to_rdf("turtle")
        # Subject: <https://example.org/datasets/2024/climate-data>

    Notes
    -----
    The *base_uri* argument from the serialiser is ignored; the template is
    always used as-is.
    """

    def __init__(self, template: str) -> None:
        self.template = template

    def __call__(
        self,
        model: RdfBaseModel,
        *,
        base_uri: str | None = None,  # noqa: ARG002
    ) -> URIRef | BNode:
        """Generate a URI from the template, substituting model field values."""
        # Build a dict of only non-None field values (as strings)
        values: dict[str, Any] = {k: str(v) for k, v in model.model_dump().items() if v is not None}
        try:
            uri = self.template.format_map(values)
        except KeyError:
            # A required placeholder has no value — fall back to BNode
            return BNode()
        return URIRef(uri)


class HashUriGenerator:
    """URI generator that creates deterministic, content-addressable URIs.

    Computes a stable hash of the specified model fields and appends it to a
    base namespace, producing a reproducible URI regardless of insert order or
    serialisation time.

    This is particularly useful when:

    * No natural identifier exists in the data.
    * You want to deduplicate resources across separate serialisations.
    * You need stable URIs without assigning them explicitly.

    Parameters
    ----------
    namespace : str | Namespace
        The base URI namespace to prepend to the hash digest, e.g.
        ``"https://example.org/hash/"`` or ``Namespace("https://example.org/hash/")``.
        A trailing ``/`` is added automatically if absent.
    fields : list[str]
        Names of the model fields to include in the hash, in order.  Fields
        with ``None`` values are skipped.  If *no* field has a value, a
        :class:`~rdflib.BNode` is returned.
    algorithm : str
        Hash algorithm name accepted by :func:`hashlib.new`.  Default is
        ``"sha256"``.  Use ``"sha1"`` for shorter (but collision-prone) digests.

    Examples
    --------
    ::

        from dartfx.rdf.pydantic import RdfBaseModel
        from dartfx.rdf.pydantic._uri_generators import HashUriGenerator

        class Publication(RdfBaseModel):
            rdf_uri_generator = HashUriGenerator(
                namespace="https://example.org/pub/",
                fields=["doi", "title"],
            )

            doi: str | None = None
            title: str | None = None

        pub = Publication(doi="10.1234/example", title="My Paper")
        # Subject: <https://example.org/pub/<sha256-of-doi+title>>

    Notes
    -----
    Field values are concatenated with ``"|"`` as a separator before hashing.
    The *base_uri* argument from the serialiser is ignored; ``namespace``
    always takes precedence.
    """

    _SEPARATOR = "|"

    def __init__(
        self,
        namespace: str | Namespace,
        fields: list[str],
        *,
        algorithm: str = "sha256",
    ) -> None:
        self.namespace = str(namespace).rstrip("/") + "/"
        self.fields = fields
        self.algorithm = algorithm

    def __call__(
        self,
        model: RdfBaseModel,
        *,
        base_uri: str | None = None,  # noqa: ARG002
    ) -> URIRef | BNode:
        """Generate a hash-based URI from the specified model fields."""
        parts = [str(getattr(model, field)) for field in self.fields if getattr(model, field, None) is not None]
        if not parts:
            return BNode()
        content = self._SEPARATOR.join(parts)
        digest = hashlib.new(self.algorithm, content.encode()).hexdigest()
        return URIRef(self.namespace + digest)


class CompositeUriGenerator:
    """URI generator that tries multiple generators in priority order.

    Returns the result of the **first** generator that produces a
    :class:`~rdflib.URIRef`.  Falls back to a :class:`~rdflib.BNode` only
    if every generator in the chain returns a BNode.

    This is useful for expressing fallback strategies:

    * "Use the ``doi`` field if set, otherwise hash the title, otherwise BNode."
    * "Use a custom generator for known types, fall back to default otherwise."

    Parameters
    ----------
    *generators : RdfUriGenerator
        Generators to try in order.  Must accept the standard
        ``(model, *, base_uri=None) -> URIRef | BNode`` signature.

    Examples
    --------
    ::

        from dartfx.rdf.pydantic import DefaultUriGenerator
        from dartfx.rdf.pydantic._uri_generators import (
            CompositeUriGenerator,
            HashUriGenerator,
        )

        gen = CompositeUriGenerator(
            DefaultUriGenerator(auto_uuid=False),          # use id if set, else BNode
            HashUriGenerator("https://example.org/h/", ["title"]),  # hash fallback
        )

        class Article(RdfBaseModel):
            rdf_uri_generator = gen
            title: str | None = None
    """

    def __init__(self, *generators: RdfUriGenerator) -> None:
        self.generators = generators

    def __call__(
        self,
        model: RdfBaseModel,
        *,
        base_uri: str | None = None,
    ) -> URIRef | BNode:
        """Try each generator in order; return the first URIRef result."""
        for generator in self.generators:
            result = generator(model, base_uri=base_uri)
            if isinstance(result, URIRef):
                return result
        return BNode()


class PrefixedUriGenerator:
    """URI generator that concatenates a fixed prefix with a single field value.

    A lightweight convenience alternative to :class:`TemplateUriGenerator` when
    the URI is simply ``<prefix><field_value>``.

    Parameters
    ----------
    prefix : str | Namespace
        The URI prefix.  A trailing ``/`` is added automatically if absent.
    field : str
        The model field whose value is appended to the prefix.  If the field
        is ``None`` or absent, a :class:`~rdflib.BNode` is returned.

    Examples
    --------
    ::

        from dartfx.rdf.pydantic._uri_generators import PrefixedUriGenerator

        class Concept(RdfBaseModel):
            rdf_uri_generator = PrefixedUriGenerator(
                prefix="https://vocab.example.org/concepts/",
                field="code",
            )
            code: str | None = None
            label: str | None = None

        c = Concept(code="001", label="Agriculture")
        # Subject: <https://vocab.example.org/concepts/001>

    Notes
    -----
    The *base_uri* argument from the serialiser is ignored; ``prefix`` always
    takes precedence.
    """

    def __init__(self, prefix: str | Namespace, field: str) -> None:
        self.prefix = str(prefix).rstrip("/") + "/"
        self.field = field

    def __call__(
        self,
        model: RdfBaseModel,
        *,
        base_uri: str | None = None,  # noqa: ARG002
    ) -> URIRef | BNode:
        """Generate a URI as prefix + field value."""
        value = getattr(model, self.field, None)
        if value is None:
            return BNode()
        return URIRef(self.prefix + str(value))
