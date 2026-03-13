Pydantic ↔ RDF Integration
==========================

The :mod:`dartfx.rdf.pydantic` module adds a thin mixin that lets you
annotate Pydantic models with RDF metadata, build `rdflib.Graph` instances, and
reconstruct the models from existing graphs. This page walks through the most
important building blocks and patterns.

Quick start
-----------

1. Import :class:`~dartfx.rdf.pydantic.RdfBaseModel` and
   :class:`~dartfx.rdf.pydantic.RdfProperty`.
2. Define a namespace for your resources and declare any prefixes you want to be
   emitted in the resulting graph.
3. Annotate each serialisable field with an RDF predicate.

.. code-block:: python

   from typing import Annotated, List

   from rdflib import Namespace, URIRef

   from dartfx.rdf.pydantic import RdfBaseModel, RdfProperty

   EX = Namespace("https://example.org/ns/")


   class Organisation(RdfBaseModel):
       rdf_type = EX.Organisation
       rdf_namespace = EX
       rdf_prefixes = {"ex": EX}

       id: str
       name: Annotated[str, RdfProperty(EX.name)]
       homepage: Annotated[URIRef, RdfProperty(EX.homepage)]
       keywords: Annotated[List[str], RdfProperty(EX.keyword)]


   org = Organisation(
       id="toolkit",
       name="RDF Toolkit",
       homepage=URIRef("https://example.org/toolkit"),
       keywords=["python", "metadata"],
   )

   turtle = org.to_rdf(format="turtle")

``RdfBaseModel`` takes care of creating a subject identifier, emitting RDF
triples for every annotated field, and binding the default prefixes. The graph
returned by :meth:`~dartfx.rdf.pydantic.RdfBaseModel.to_rdf_graph` can be
serialised in any format supported by `rdflib`.

Mapping rules
-------------

* The ``predicate`` argument on :class:`~dartfx.rdf.pydantic.RdfProperty`
  can be either a full ``rdflib.term.URIRef`` or a string. Strings will be
  coerced into ``URIRef`` instances at runtime.
* A model-level ``rdf_type`` constant adds ``rdf:type`` triples for every
  instance.
* If ``rdf_namespace`` is defined and the model exposes an ``id`` value (or the
  field configured via ``rdf_id_field``), the identifier is appended to the
  namespace. Absolute identifiers, such as UUID URNs or HTTP URLs, are used as
  provided.
* Lists of annotated fields are emitted as repeated predicate/object pairs. The
  same applies to nested ``RdfBaseModel`` subclasses, which are recursively
  serialised.

Reading data back
-----------------

Instances can be rehydrated from either a graph object or a textual
serialisation.

.. code-block:: python

   clone = Organisation.from_rdf(turtle, format="turtle")
   assert clone == org

When a model sets ``rdf_type`` the parser uses it to locate the correct subject
in the graph. Otherwise it expects the graph to contain exactly one subject and
raises an error if there are multiple candidates. You can always bypass the
heuristics by passing the ``subject`` keyword argument to
:meth:`~dartfx.rdf.pydantic.RdfBaseModel.from_rdf_graph` or
:meth:`~dartfx.rdf.pydantic.RdfBaseModel.from_rdf`.

Language tags and localized strings
-----------------------------------

The toolkit provides first-class support for RDF language-tagged literals through
three complementary types:

* :class:`~dartfx.rdf.pydantic.LangString` – a single value/language-tag pair.
* :class:`~dartfx.rdf.pydantic.LangStringList` – an ordered, deduplicated
  collection of ``LangString`` items with convenience query and mutation methods.
* :data:`~dartfx.rdf.pydantic.LocalizedStr` – a Pydantic-aware type alias that
  coerces flexible inputs into a ``LangStringList`` automatically.

.. contents::
   :local:
   :depth: 2

LangString
^^^^^^^^^^

``LangString`` is a lightweight, frozen Pydantic model representing a single
string value with an optional language tag.

.. code-block:: python

   from dartfx.rdf.pydantic import LangString

   tagged   = LangString(value="Hello", lang="en")
   untagged = LangString(value="Plain text")          # lang defaults to None

   str(tagged)     # "Hello"
   repr(tagged)    # '"Hello"@en'
   repr(untagged)  # '"Plain text"'

``LangString`` instances are hashable and comparable:

.. code-block:: python

   tagged == LangString(value="Hello", lang="en")  # True
   tagged == LangString(value="Hello", lang="fr")  # False

   # Usable in sets and as dict keys
   labels = {tagged, untagged}

LocalizedStr – flexible input, canonical storage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``LocalizedStr`` is the recommended type for any field that may carry
language-tagged literals. You annotate your model field with it and provide
input in whichever form is most convenient — the validator coerces everything
into a canonical ``LangStringList``.

**Accepted input types:**

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Input
     - Stored as
   * - ``"Plain text"``
     - ``LangStringList([LangString(value="Plain text", lang=None)])``
   * - ``LangString(value="Hello", lang="en")``
     - ``LangStringList([LangString(value="Hello", lang="en")])``
   * - ``{"en": "World", "es": "Mundo"}``
     - ``LangStringList([LangString("World","en"), LangString("Mundo","es")])``
   * - ``{"en": ["Earth", "World"]}``
     - ``LangStringList([LangString("Earth","en"), LangString("World","en")])``
   * - ``["Plain", LangString("Hi","en")]``
     - ``LangStringList([LangString("Plain",None), LangString("Hi","en")])``

Duplicate ``(value, lang)`` pairs are silently dropped, preserving insertion
order.

**Example – defining a model:**

.. code-block:: python

   from typing import Annotated
   from rdflib import SKOS
   from dartfx.rdf.pydantic import RdfBaseModel, RdfProperty, LocalizedStr, LangString

   EX = Namespace("https://example.org/ns/")

   class Concept(RdfBaseModel):
       rdf_type = SKOS.Concept
       rdf_namespace = EX

       id: str
       pref_label: Annotated[LocalizedStr | None, RdfProperty(SKOS.prefLabel)] = None

   # 1. Using a dictionary (recommended for multi-language)
   c1 = Concept(id="c1", pref_label={"en": "World", "es": "Mundo"})

   # 2. Using explicit LangString
   c2 = Concept(id="c2", pref_label=LangString(value="Hello", lang="en"))

   # 3. Using plain strings
   c3 = Concept(id="c3", pref_label="Plain text")

   # 4. Multiple values per language
   c4 = Concept(id="c4", pref_label={"en": ["Earth", "World"]})

   # 5. Mixed-type list
   c5 = Concept(id="c5", pref_label=[
       "Plain string",
       LangString(value="Hello", lang="en"),
       LangString(value="Bonjour", lang="fr"),
   ])

Str-like behaviour
""""""""""""""""""

When a ``LangStringList`` contains only **one entry**, or exactly **one
untagged entry** among tagged ones, it behaves as a plain ``str`` for
comparison and string conversion:

.. code-block:: python

   c = Concept(id="c1", pref_label="Hello")
   str(c.pref_label)        # "Hello"
   c.pref_label == "Hello"  # True

   # One untagged entry among tagged
   c = Concept(id="c2", pref_label=[
       "Plain",
       LangString(value="Hola", lang="es"),
   ])
   str(c.pref_label)        # "Plain"
   c.pref_label == "Plain"  # True

   # List comparison still works normally
   c.pref_label == [LangString(value="Plain", lang=None),
                     LangString(value="Hola", lang="es")]  # True

LangStringList – query methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``LangStringList`` extends ``list[LangString]`` with dedicated helpers for
inspecting localized values.

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Method
     - Description
   * - ``len(ls)``
     - Total number of entries.
   * - ``ls.count_by_lang("en")``
     - Count entries for a language tag. Use ``None`` or ``""`` for untagged.
   * - ``ls.has_language("en")``
     - ``True`` if at least one entry has the given tag.
   * - ``ls.has_language(None)``
     - ``True`` if untagged entries exist.
   * - ``ls.has_untagged()``
     - Shorthand for ``has_language(None)``.
   * - ``ls.has_synonyms("en")``
     - ``True`` if the language has more than one entry.
   * - ``ls.languages()``
     - Set of distinct language tags (including ``None``).
   * - ``ls.untagged()``
     - ``LangStringList`` with only untagged entries.
   * - ``ls.get_by_language("en")``
     - ``LangStringList`` filtered to a specific language tag.

.. code-block:: python

   labels = c1.pref_label  # {"en": "World", "es": "Mundo"}
   labels.languages()              # {"en", "es"}
   labels.has_language("en")       # True
   labels.count_by_lang("en")      # 1
   labels.get_by_language("es")    # LangStringList([LangString("Mundo","es")])

LangStringList – mutations
^^^^^^^^^^^^^^^^^^^^^^^^^^

All mutations automatically coerce flexible inputs and enforce ``(value, lang)``
uniqueness. Duplicate additions are silently ignored.

.. code-block:: python

   from dartfx.rdf.pydantic import LangString
   from dartfx.rdf.pydantic.skos import Concept

   c = Concept(id="c1", pref_label="Hello")
   # → LangStringList(["Hello"])

   # --- Addition ---

   # += with a single LangString
   c.pref_label += LangString(value="Hola", lang="es")
   # → ["Hello", "Hola"@es]

   # += with a list of LangStrings
   c.pref_label += [LangString(value="Bonjour", lang="fr"),
                     LangString(value="Welt", lang="de")]
   # → ["Hello", "Hola"@es, "Bonjour"@fr, "Welt"@de]

   # .append() works the same way
   c.pref_label.append(LangString(value="Ciao", lang="it"))
   # → ["Hello", "Hola"@es, "Bonjour"@fr, "Welt"@de, "Ciao"@it]

   # Duplicates are silently ignored
   c.pref_label += LangString(value="Hello", lang=None)
   len(c.pref_label)  # still 5

   # + returns a new copy (original untouched)
   bigger = c.pref_label + [LangString(value="Olá", lang="pt")]
   len(bigger)         # 6
   len(c.pref_label)   # still 5

   # --- Subtraction ---

   # -= removes matching (value, lang) entries in-place
   c.pref_label -= LangString(value="Hola", lang="es")
   # → ["Hello", "Bonjour"@fr, "Welt"@de, "Ciao"@it]

   # - returns a new copy with the entry removed
   without_fr = c.pref_label - LangString(value="Bonjour", lang="fr")
   len(without_fr)     # 3 – "Bonjour"@fr removed
   len(c.pref_label)   # 4 – original unchanged

   # Non-matching subtractions are safe (no error)
   c.pref_label -= LangString(value="Nonexistent", lang="xx")
   len(c.pref_label)   # still 4

RDF round-trip
""""""""""""""

``LocalizedStr`` fields are serialised to standard RDF language-tagged literals
and deserialised back into ``LangStringList`` automatically:

.. code-block:: python

   c = Concept(id="c1", pref_label={"en": "World", "es": "Mundo"})
   graph = c.to_rdf_graph()

   # Produces:
   #   <.../c1> skos:prefLabel "World"@en, "Mundo"@es .

   restored = Concept.from_rdf_graph(graph, subject)
   assert restored.pref_label.has_language("en")
   assert restored.pref_label == c.pref_label


Custom Datatypes
----------------

``RdfProperty`` accepts an optional ``datatype`` parameter to fine-tune literal
serialisation. Datatypes may be defined as strings, namespace terms, or full
``URIRef`` instances.

Handle URIs specifically by choosing between resource identifiers or typed literals:

* **Resource identifiers**: Use ``rdflib.URIRef`` as the field type. The toolkit
  will ensure these are emitted as URI nodes in the graph.
* **XSD.anyURI literals**: Use ``str`` (or Pydantic's ``AnyUrl``) and set
  ``datatype=XSD.anyURI``. This emits a literal with an explicit datatype.

.. code-block:: python

   from pydantic import AnyUrl
   from rdflib import XSD, SCHEMA, URIRef


   class Dataset(RdfBaseModel):
       rdf_type = EX.Dataset
       rdf_namespace = EX

       id: str
       created: Annotated[str, RdfProperty(EX.created, datatype=XSD.date)]
       # Serialized as a URI Resource
       see_also: Annotated[URIRef | None, RdfProperty(SCHEMA.seeAlso)] = None
       # Serialized as "..."^^xsd:anyURI
       download_url: Annotated[AnyUrl | None, RdfProperty(SCHEMA.downloadUrl, datatype=XSD.anyURI)] = None


   dataset = Dataset(
       id="demo",
       title="Example",
       created="2024-03-01",
       see_also=URIRef("https://example.org/docs"),
       download_url="https://example.org/files/data.zip"
   )

   graph = dataset.to_rdf_graph()

Custom serialisation hooks
--------------------------

When you need more control, ``RdfProperty`` allows you to pass ``serializer``
and ``parser`` callables. ``serializer`` receives the field value and must
return an ``rdflib`` node; ``parser`` runs during deserialisation and receives
whatever node was found in the graph.

.. code-block:: python

   def to_uppercase(value: str) -> str:
       return value.upper()


   def parse_lower(node) -> str:
       return str(node).lower()


   class TaggedConcept(RdfBaseModel):
       rdf_type = EX.Concept
       rdf_namespace = EX

       id: str
       label: Annotated[
           str,
           RdfProperty(EX.label, serializer=to_uppercase, parser=parse_lower),
       ]


   concept = TaggedConcept(id="term", label="Toolkit")
   round_trip = TaggedConcept.from_rdf(concept.to_rdf())
   assert round_trip.label == "toolkit"

Advanced scenarios
------------------

* Override ``rdf_id_field`` if your identifier lives on a different field name.
* Supply ``rdf_prefixes`` to bind additional prefixes on the emitted graph.
* Set ``base_uri`` when serialising or parsing if you want generated identifiers
  to be relative to an external namespace instead of ``rdf_namespace``.

The tests in :mod:`tests.test_pydantic_rdf` provide additional examples that
cover nested resources, optional values, and custom datatypes.


Subject URI generation
----------------------

By default, :class:`~dartfx.rdf.pydantic.RdfBaseModel` delegates subject URI
creation to a :class:`~dartfx.rdf.pydantic.RdfUriGenerator` — a simple
:py:class:`typing.Protocol` satisfied by any callable with the signature::

    (model: RdfBaseModel, *, base_uri: str | None = None) -> URIRef | BNode

The default strategy is :class:`~dartfx.rdf.pydantic.DefaultUriGenerator`,
which resolves a subject in the following order:

1. If ``rdf_id_field`` is set and non-``None``: build a URI from the value
   (prepend namespace / base_uri, or use as-is if already an absolute URI).
2. If no identifier: mint a UUID URI (``auto_uuid=True``).
3. If ``auto_uuid=False``: return a :class:`~rdflib.BNode`.

.. note::

   **Why** ``auto_uuid=True`` **is the default**

   Strictly speaking, an anonymous resource should be a Blank Node.  However,
   UUID URIs are the practical default because they:

   * travel across graph boundaries (BNodes cannot),
   * survive round-trips through parse/serialise cycles, and
   * never collide when two graphs are merged.

   Use ``DefaultUriGenerator(auto_uuid=False)`` when you explicitly want
   anonymous, locally-scoped resources (e.g. reified statements).


Replacing the default generator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Assign any :class:`~dartfx.rdf.pydantic.RdfUriGenerator` to the
``rdf_uri_generator`` field — either at the **class level** (as a default for
all instances) or at the **instance level** (to override per object):

.. code-block:: python

   from dartfx.rdf.pydantic import RdfBaseModel, DefaultUriGenerator

   # Class-level: all instances use BNodes unless they have an id
   class Statement(RdfBaseModel):
       rdf_uri_generator = DefaultUriGenerator(auto_uuid=False)
       ...

   # Instance-level: one specific object gets a custom generator
   person = Person(
       id="alice",
       rdf_uri_generator=lambda model, *, base_uri=None: EX[type(model).__name__],
   )

You can also pass a generator at call-site, which takes priority over the
instance:

.. code-block:: python

   graph = person.to_rdf_graph(rdf_uri_generator=my_call_site_generator)


Built-in generators
^^^^^^^^^^^^^^^^^^^

The :mod:`~dartfx.rdf.pydantic._uri_generators` module provides four
ready-to-use implementations beyond :class:`~dartfx.rdf.pydantic.DefaultUriGenerator`.
All are exported from ``dartfx.rdf.pydantic``.

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Generator
     - Use when…
   * - :class:`~dartfx.rdf.pydantic.TemplateUriGenerator`
     - The URI shape is known and model fields supply the parts.
   * - :class:`~dartfx.rdf.pydantic.HashUriGenerator`
     - No stable id; need deterministic, content-addressable URIs.
   * - :class:`~dartfx.rdf.pydantic.CompositeUriGenerator`
     - Multiple strategies needed with a clear priority order.
   * - :class:`~dartfx.rdf.pydantic.PrefixedUriGenerator`
     - Lightest option: just ``prefix + field_value``.


TemplateUriGenerator
""""""""""""""""""""

Builds URIs from a Python format-string where ``{field_name}`` placeholders
are replaced by model field values.  Returns a :class:`~rdflib.BNode` if a
required field is ``None``.

.. code-block:: python

   from dartfx.rdf.pydantic import TemplateUriGenerator

   class Dataset(RdfBaseModel):
       rdf_type = EX.Dataset
       rdf_uri_generator = TemplateUriGenerator(
           "https://example.org/datasets/{year}/{slug}"
       )
       year: int | None = None
       slug: str | None = None

   ds = Dataset(year=2024, slug="climate")
   # Subject: <https://example.org/datasets/2024/climate>


HashUriGenerator
""""""""""""""""

Produces a deterministic URI by hashing the concatenated values of specified
model fields.  Useful for deduplication across separate serialisations.

.. code-block:: python

   from dartfx.rdf.pydantic import HashUriGenerator

   class Publication(RdfBaseModel):
       rdf_uri_generator = HashUriGenerator(
           namespace="https://example.org/pub/",
           fields=["doi", "title"],
           algorithm="sha256",  # default
       )
       doi: str | None = None
       title: str | None = None

   pub = Publication(doi="10.1234/ex", title="My Paper")
   # Subject: <https://example.org/pub/<sha256-digest>>

The hash is computed over ``"|".join(str(v) for v in fields if v is not None)``.
Returns a :class:`~rdflib.BNode` if all specified fields are ``None``.


CompositeUriGenerator
"""""""""""""""""""""

Tries a sequence of generators in order and returns the result of the first
one that produces a :class:`~rdflib.URIRef`.  Falls back to
:class:`~rdflib.BNode` if all generators fail.

.. code-block:: python

   from dartfx.rdf.pydantic import (
       CompositeUriGenerator,
       DefaultUriGenerator,
       HashUriGenerator,
   )

   gen = CompositeUriGenerator(
       DefaultUriGenerator(auto_uuid=False),      # use id if set, else try next
       HashUriGenerator("https://example.org/h/", ["title"]),
   )

   class Article(RdfBaseModel):
       rdf_uri_generator = gen
       id: str | None = None
       title: str | None = None


PrefixedUriGenerator
""""""""""""""""""""

The simplest option: concatenates a fixed prefix with the value of a single
model field.

.. code-block:: python

   from dartfx.rdf.pydantic import PrefixedUriGenerator

   class Concept(RdfBaseModel):
       rdf_uri_generator = PrefixedUriGenerator(
           prefix="https://vocab.example.org/concepts/",
           field="code",
       )
       code: str | None = None
       label: str | None = None

   c = Concept(code="001", label="Agriculture")
   # Subject: <https://vocab.example.org/concepts/001>

Returns a :class:`~rdflib.BNode` when the field value is ``None``.


Custom generators
^^^^^^^^^^^^^^^^^

Any callable with the right signature qualifies:

.. code-block:: python

   from rdflib import URIRef, BNode
   from dartfx.rdf.pydantic import RdfBaseModel, RdfUriGenerator

   def my_generator(
       model: RdfBaseModel,
       *,
       base_uri: str | None = None,
   ) -> URIRef | BNode:
       return EX[f"{type(model).__name__}/{model.id}"]

   assert isinstance(my_generator, RdfUriGenerator)  # True — protocol is runtime-checkable

   # Or as a class with __call__:
   class MyGenerator:
       def __call__(
           self,
           model: RdfBaseModel,
           *,
           base_uri: str | None = None,
       ) -> URIRef | BNode:
           ...
