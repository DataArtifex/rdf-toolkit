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
:meth:`~dartfx.rdf.pydantic.rdf.RdfBaseModel.from_rdf_graph` or
:meth:`~dartfx.rdf.pydantic.rdf.RdfBaseModel.from_rdf`.

Language tags and datatypes
---------------------------

``RdfProperty`` accepts optional ``datatype`` and ``language`` parameters to
fine-tune literal serialisation. Datatypes may be defined as strings, namespace
terms, or full ``URIRef`` instances.

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
       title: Annotated[str, RdfProperty(EX.title, language="en")]
       created: Annotated[str, RdfProperty(EX.created, datatype=XSD.date)]
       # Serialized as a URI Resource
       see_also: Annotated[Optional[URIRef], RdfProperty(SCHEMA.seeAlso)] = None
       # Serialized as "..."^^xsd:anyURI
       download_url: Annotated[Optional[AnyUrl], RdfProperty(SCHEMA.downloadUrl, datatype=XSD.anyURI)] = None


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
