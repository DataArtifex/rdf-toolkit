"""Pydantic RDF Base Model - Bridge between Pydantic models and RDF graphs.

This module provides a base class and utilities for seamlessly converting Pydantic models
to and from RDF (Resource Description Framework) graphs using rdflib. It enables type-safe,
validated RDF data modeling with automatic serialization and deserialization.

The core components are:

- :class:`RdfBaseModel`: A Pydantic BaseModel subclass that provides RDF serialization
  and deserialization capabilities. Models inheriting from this class can be automatically
  converted to/from RDF graphs in various formats (Turtle, RDF/XML, JSON-LD, etc.).

- :class:`RdfProperty`: A metadata descriptor used in type annotations to map Pydantic
  fields to RDF predicates, with optional datatype and language specifications.

Basic Usage
-----------

Define a model by inheriting from RdfBaseModel and annotating fields with RdfProperty::

    from typing import Annotated, Optional, List
    from rdflib import Namespace, URIRef
    from dartfx.rdf.pydantic import RdfBaseModel, RdfProperty

    FOAF = Namespace("http://xmlns.com/foaf/0.1/")

    class Person(RdfBaseModel):
        rdf_type: str = str(FOAF.Person)
        rdf_namespace = FOAF
        rdf_prefixes = {"foaf": FOAF}

        name: Annotated[Optional[List[str]], RdfProperty(FOAF.name)] = None
        email: Annotated[Optional[List[str]], RdfProperty(FOAF.mbox)] = None
        knows: Annotated[Optional[List[URIRef | Person]], RdfProperty(FOAF.knows)] = None

Serialize to RDF::

    person = Person(name=["Alice"], email=["alice@example.org"])
    turtle = person.to_rdf("turtle")
    # Output: Turtle format RDF with proper namespace bindings

Deserialize from RDF::

    restored = Person.from_rdf(turtle, format="turtle")
    assert restored.name == ["Alice"]

Key Features
------------

- **Type Safety**: Full Pydantic validation for RDF data
- **Multiple Formats**: Serialize to Turtle, RDF/XML, JSON-LD, N-Triples, etc.
- **Round-trip Support**: Lossless conversion between Python objects and RDF
- **Nested Objects**: Support for nested RdfBaseModel instances
- **List Values**: Automatic handling of multi-valued properties
- **Custom Datatypes**: Specify XSD datatypes and language tags
- **Namespace Management**: Automatic prefix binding for clean serialization
- **Flexible Identifiers**: Use custom ID fields or auto-generate UUIDs

Advanced Features
-----------------

Custom serializers and parsers::

    def serialize_date(d: date) -> str:
        return d.isoformat()

    def parse_date(node: Literal) -> date:
        return date.fromisoformat(str(node))

    birth_date: Annotated[Optional[date], RdfProperty(
        SCHEMA.birthDate,
        serializer=serialize_date,
        parser=parse_date
    )] = None

Language-tagged literals::

    description: Annotated[Optional[List[str]], RdfProperty(
        DC.description,
        language="en"
    )] = None

Custom datatypes::

    age: Annotated[Optional[int], RdfProperty(
        FOAF.age,
        datatype=XSD.integer
    )] = None

Examples
--------

Simple metadata example::

    from rdflib import Namespace, DCTERMS

    class Document(RdfBaseModel):
        rdf_namespace = DCTERMS
        rdf_prefixes = {"dcterms": DCTERMS}

        title: Annotated[Optional[List[str]], RdfProperty(DCTERMS.title)] = None
        creator: Annotated[Optional[List[str]], RdfProperty(DCTERMS.creator)] = None

    doc = Document(title=["My Document"], creator=["John Doe"])
    print(doc.to_rdf("turtle"))

Nested objects example::

    class Organization(RdfBaseModel):
        rdf_type: str = str(FOAF.Organization)
        name: Annotated[Optional[List[str]], RdfProperty(FOAF.name)] = None

    class Person(RdfBaseModel):
        rdf_type: str = str(FOAF.Person)
        name: Annotated[Optional[List[str]], RdfProperty(FOAF.name)] = None
        works_for: Annotated[Optional[List[Organization]], RdfProperty(FOAF.workplaceHomepage)] = None

    org = Organization(name=["ACME Corp"])
    person = Person(name=["Alice"], works_for=[org])
    # Both person and organization are serialized to the graph

Notes
-----

- Field names don't need to match RDF predicate names - use RdfProperty to map them
- Use `Optional[List[T]]` for multi-valued properties (standard in RDF)
- The `id` field is special and maps to the RDF subject URI
- Custom `rdf_id_field` can be specified per model
- Auto-generated UUIDs are used when no ID is provided
- Namespace prefixes improve readability of serialized output

See Also
--------

- rdflib documentation: https://rdflib.readthedocs.io/
- Pydantic documentation: https://docs.pydantic.dev/
- RDF Primer: https://www.w3.org/TR/rdf11-primer/
"""

from __future__ import annotations

import re
import types
import uuid
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import (
    Annotated,
    Any,
    ClassVar,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

from pydantic import BaseModel, ConfigDict, Field
from rdflib import RDF, XSD, BNode, Graph, Literal, Namespace, URIRef

T = TypeVar("T", bound="RdfBaseModel")


class LangString(BaseModel):
    """A string with an optional language tag.

    This class is used to represent RDF language-tagged literals in Pydantic
    models. It provides a structured way to handle localized strings while
    maintaining compatibility with Pydantic validation.

    Attributes
    ----------
    value : str
        The string content of the literal.
    lang : str | None, optional
        The language tag (e.g., "en", "fr", "de"). Default is None.
    """

    value: str
    lang: str | None = None

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        if self.lang:
            return f'"{self.value}"@{self.lang}'
        return f'"{self.value}"'

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            return self.value == other
        if isinstance(other, LangString):
            return self.value == other.value and self.lang == other.lang
        return super().__eq__(other)

    def __hash__(self) -> int:
        return hash((self.value, self.lang))


LocalizedStr = str | LangString | list[str | LangString] | dict[str, str | list[str]]


@dataclass(frozen=True)
class RdfProperty:
    """Metadata descriptor for mapping Pydantic fields to RDF predicates.

    This class is used as metadata in type annotations to specify how a Pydantic
    field should be serialized to and deserialized from RDF. It provides control
    over the RDF predicate URI, datatype, language tags, and custom serialization.

    Parameters
    ----------
    predicate : str | URIRef
        The RDF predicate URI for this property. Can be a string URI or an
        rdflib URIRef. Typically uses a namespace property like `FOAF.name`.

    datatype : str | URIRef | None, optional
        The XSD datatype URI for literal values. If None, the datatype is
        inferred from the Python type. Examples: XSD.string, XSD.integer,
        XSD.dateTime. Default is None.

    language : str | None, optional
        The language tag for string literals (e.g., "en", "fr", "de").
        Creates language-tagged RDF literals. Cannot be used with datatype.
        Default is None.

    serializer : Callable | None, optional
        A custom function to transform Python values before RDF serialization.
        Signature: (value: Any) -> Any. The returned value should be compatible
        with RDF serialization (str, int, URIRef, Literal, etc.).
        Default is None.

    parser : Callable | None, optional
        A custom function to transform RDF nodes back to Python values during
        deserialization. Signature: (node: URIRef | Literal) -> Any.
        Default is None.

    Attributes
    ----------
    predicate : str | URIRef
        The RDF predicate URI.
    datatype : str | URIRef | None
        The XSD datatype URI for literals.
    language : str | None
        The language tag for string literals.
    serializer : Callable | None
        Custom serialization function.
    parser : Callable | None
        Custom parsing function.

    Methods
    -------
    predicate_uri() -> URIRef
        Convert the predicate to an rdflib URIRef.
    datatype_uri() -> URIRef | None
        Convert the datatype to an rdflib URIRef, or None if not specified.

    Examples
    --------
    Basic property mapping::

        from rdflib import FOAF
        from typing import Annotated, Optional, List

        name: Annotated[Optional[List[str]], RdfProperty(FOAF.name)] = None

    With datatype::

        from rdflib import XSD

        age: Annotated[Optional[int], RdfProperty(
            FOAF.age,
            datatype=XSD.integer
        )] = None

    With language tag::

        description: Annotated[Optional[List[str]], RdfProperty(
            DCTERMS.description,
            language="en"
        )] = None

    With custom serializer/parser::

        from datetime import date

        def serialize_date(d: date) -> str:
            return d.isoformat()

        def parse_date(node) -> date:
            return date.fromisoformat(str(node))

        birth_date: Annotated[Optional[date], RdfProperty(
            SCHEMA.birthDate,
            serializer=serialize_date,
            parser=parse_date
        )] = None

    Notes
    -----
    - RdfProperty instances are immutable (frozen dataclass)
    - Use in Annotated type hints as metadata
    - Language and datatype are mutually exclusive
    - Custom serializers/parsers override default behavior
    - The predicate URI is the only required parameter

    See Also
    --------
    RdfBaseModel : Base class for RDF-enabled Pydantic models
    """

    predicate: str | URIRef
    datatype: str | URIRef | None = None
    language: str | None = None
    serializer: Any | None = None
    parser: Any | None = None

    def predicate_uri(self) -> URIRef:
        """Convert the predicate to an rdflib URIRef.

        Returns
        -------
        URIRef
            The predicate as an rdflib URIRef.

        Examples
        --------
        >>> from rdflib import FOAF
        >>> prop = RdfProperty(FOAF.name)
        >>> prop.predicate_uri()
        rdflib.term.URIRef('http://xmlns.com/foaf/0.1/name')
        """
        result = _ensure_uri(self.predicate)
        assert result is not None  # predicate is required, so this should never be None
        return result

    def datatype_uri(self) -> URIRef | None:
        """Convert the datatype to an rdflib URIRef.

        Returns
        -------
        URIRef | None
            The datatype as an rdflib URIRef, or None if no datatype is specified.

        Examples
        --------
        >>> from rdflib import XSD
        >>> prop = RdfProperty(FOAF.age, datatype=XSD.integer)
        >>> prop.datatype_uri()
        rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#integer')
        """
        return _ensure_uri(self.datatype)


class RdfBaseModel(BaseModel):
    """Base class for Pydantic models with RDF serialization capabilities.

    This class extends Pydantic's BaseModel to provide automatic conversion to and
    from RDF graphs. Models inheriting from RdfBaseModel can be serialized to various
    RDF formats (Turtle, RDF/XML, JSON-LD, etc.) and deserialized back to Python objects.

    Class Attributes
    ----------------
    rdf_type : str | URIRef | None
        The RDF type (rdf:type) for instances of this class. Typically set to a
        vocabulary class URI like `FOAF.Person` or `SKOS.Concept`. If None, no
        rdf:type triple is added to the graph.

    rdf_namespace : str | Namespace | None
        The default namespace for generating subject URIs. Used when an instance
        has an `id` but not a full URI. For example, with namespace `FOAF` and
        id `"john"`, the subject becomes `<http://xmlns.com/foaf/0.1/john>`.

    rdf_id_field : str | None
        The name of the field to use for the RDF subject identifier. Defaults to
        `"id"`. Set to None to disable ID field mapping and always use UUIDs.

    rdf_prefixes : Dict[str, str | Namespace]
        Namespace prefix bindings for RDF serialization. Used to create readable
        output with prefixes like `foaf:name` instead of full URIs. Automatically
        includes 'rdf' and 'xsd' prefixes.

    Instance Attributes
    -------------------
    id : Any, optional
        If `rdf_id_field` is "id" (default), this field contains the subject
        identifier. Can be a short string (combined with namespace) or a full URI.

    Methods
    -------
    to_rdf_graph(graph=None, *, base_uri=None) -> Graph
        Serialize this model instance into an rdflib Graph.

    to_rdf(format="turtle", *, base_uri=None, **kwargs) -> str
        Serialize this model instance to an RDF string in the specified format.

    from_rdf_graph(graph, subject, *, base_uri=None) -> RdfBaseModel
        Class method to deserialize a model from an RDF graph.

    from_rdf(data, *, format="turtle", subject=None, base_uri=None) -> RdfBaseModel
        Class method to deserialize a model from an RDF string or bytes.

    Configuration
    -------------
    The model_config allows arbitrary types (URIRef, Literal, etc.) in fields.

    Examples
    --------
    Basic model definition::

        from rdflib import Namespace, FOAF
        from typing import Annotated, Optional, List

        class Person(RdfBaseModel):
            rdf_type: str = str(FOAF.Person)
            rdf_namespace = FOAF
            rdf_prefixes = {"foaf": FOAF}

            name: Annotated[Optional[List[str]], RdfProperty(FOAF.name)] = None
            email: Annotated[Optional[List[str]], RdfProperty(FOAF.mbox)] = None

    Creating and serializing::

        person = Person(name=["Alice Smith"], email=["alice@example.org"])
        turtle_output = person.to_rdf("turtle")
        # Output includes proper @prefix declarations and triples

    Deserializing::

        restored = Person.from_rdf(turtle_output, format="turtle")
        assert restored.name == ["Alice Smith"]

    With custom ID::

        person = Person(id="alice", name=["Alice Smith"])
        # Subject URI becomes: <http://xmlns.com/foaf/0.1/alice>

    With full URI as ID::

        person = Person(id="http://example.org/people/alice", name=["Alice"])
        # Subject URI is: <http://example.org/people/alice>

    Nested objects::

        class Organization(RdfBaseModel):
            rdf_type: str = str(FOAF.Organization)
            name: Annotated[Optional[List[str]], RdfProperty(FOAF.name)] = None

        class Person(RdfBaseModel):
            rdf_type: str = str(FOAF.Person)
            name: Annotated[Optional[List[str]], RdfProperty(FOAF.name)] = None
            org: Annotated[Optional[List[Organization]], RdfProperty(FOAF.member)] = None

        person = Person(
            name=["Alice"],
            org=[Organization(name=["ACME Corp"])]
        )
        # Both person and organization are serialized to the graph

    Notes
    -----
    - All fields mapped to RDF should use `Annotated[..., RdfProperty(...)]`
    - Multi-valued properties use `Optional[List[T]]` (standard in RDF)
    - The `id` field is optional; if not provided, a UUID is generated
    - Nested RdfBaseModel instances are automatically serialized
    - Round-trip serialization is lossless for supported types
    - Custom serializers/parsers can handle complex types

    See Also
    --------
    RdfProperty : Metadata for field-to-predicate mapping
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    rdf_type: ClassVar[str | URIRef | None] = None
    rdf_namespace: ClassVar[str | Namespace | None] = None
    rdf_id_field: ClassVar[str | None] = "id"
    rdf_prefixes: ClassVar[dict[str, str | Namespace]] = {}

    rdf_auto_uuid: bool = Field(default=True, exclude=True)
    rdf_uri_generator: Callable[[Any], URIRef | BNode] | None = Field(default=None, exclude=True)

    def to_rdf_graph(
        self,
        graph: Graph | None = None,
        *,
        base_uri: str | None = None,
        rdf_uri_generator: Callable[[Any], URIRef | BNode] | None = None,
    ) -> Graph:
        """Serialize the model instance into an rdflib Graph.

        This method converts the Pydantic model instance into RDF triples and adds
        them to an rdflib Graph. All fields annotated with RdfProperty are converted
        to RDF predicates and objects. Nested RdfBaseModel instances are recursively
        serialized.

        Parameters
        ----------
        graph : Graph | None, optional
            An existing rdflib Graph to add triples to. If None, a new Graph is
            created. Default is None.

        base_uri : str | None, optional
            A base URI for generating subject URIs when the model doesn't have a
            full URI identifier. Used for relative identifier resolution.
            Default is None.

        rdf_uri_generator : Callable[[Any], Union[URIRef, BNode]] | None, optional
            A custom function to generate subject URIs for model instances.
            The function receives the model instance and should return an
            rdflib URIRef or BNode. This overrides the model's own
            rdf_uri_generator if provided.

        Returns
        -------
        Graph
            The rdflib Graph containing the serialized RDF triples.

        Examples
        --------
        Basic serialization::

            person = Person(name=["Alice"])
            graph = person.to_rdf_graph()
            # graph now contains triples for the person

        Adding to existing graph::

            graph = Graph()
            person1 = Person(name=["Alice"])
            person2 = Person(name=["Bob"])
            person1.to_rdf_graph(graph)
            person2.to_rdf_graph(graph)
            # graph contains triples for both persons

        With base URI::

            person = Person(id="alice", name=["Alice"])
            graph = person.to_rdf_graph(base_uri="http://example.org/people/")
            # Subject becomes: <http://example.org/people/alice>

        Notes
        -----
        - Namespace prefixes from rdf_prefixes are automatically bound
        - rdf:type triple is added if rdf_type is set
        - None values and empty lists are skipped
        - The subject URI is generated from the id field or a UUID

        See Also
        --------
        to_rdf : Serialize directly to a string format
        from_rdf_graph : Deserialize from a Graph
        """

        graph = graph if graph is not None else Graph()
        self._serialise_into_graph(graph, base_uri=base_uri, rdf_uri_generator=rdf_uri_generator)
        return graph

    def to_rdf(
        self,
        format: str = "turtle",
        *,
        base_uri: str | None = None,
        rdf_uri_generator: Callable[[Any], URIRef | BNode] | None = None,
        **kwargs: Any,
    ) -> str:
        """Serialize the model instance to an RDF string.

        This is a convenience method that creates a Graph, serializes the model
        into it, and then serializes the Graph to the specified format.

        Parameters
        ----------
        format : str, optional
            The RDF serialization format. Supported formats include:
            - "turtle" (default): Turtle/Trig format
            - "xml" or "pretty-xml": RDF/XML format
            - "json-ld": JSON-LD format
            - "nt" or "ntriples": N-Triples format
            - "n3": Notation3 format
            Default is "turtle".

        base_uri : str | None, optional
            A base URI for generating subject URIs. Default is None.

        rdf_uri_generator : Callable[[Any], Union[URIRef, BNode]] | None, optional
            A custom function to generate subject URIs for model instances.
            The function receives the model instance and should return an
            rdflib URIRef or BNode. This overrides the model's own
            rdf_uri_generator if provided.

        **kwargs : Any
            Additional keyword arguments passed to rdflib's serialize() method.

        Returns
        -------
        str
            The serialized RDF as a string.

        Examples
        --------
        Turtle format (default)::

            person = Person(name=["Alice Smith"])
            turtle = person.to_rdf("turtle")
            print(turtle)
            # @prefix foaf: <http://xmlns.com/foaf/0.1/> .
            # foaf:alice a foaf:Person ;
            #     foaf:name "Alice Smith" .

        RDF/XML format::

            xml = person.to_rdf("xml")

        JSON-LD format::

            jsonld = person.to_rdf("json-ld")

        N-Triples format::

            ntriples = person.to_rdf("ntriples")

        Notes
        -----
        - Turtle format is most human-readable with prefix support
        - Format names are case-insensitive
        - The output encoding is UTF-8

        See Also
        --------
        to_rdf_graph : Get the Graph object directly
        from_rdf : Deserialize from an RDF string
        """

        graph = self.to_rdf_graph(base_uri=base_uri, rdf_uri_generator=rdf_uri_generator)
        return graph.serialize(format=format, **kwargs)  # type: ignore[no-any-return]

    @classmethod
    def from_rdf_graph(
        cls: type[T],
        graph: Graph,
        subject: URIRef | str,
        *,
        base_uri: str | None = None,
    ) -> T:
        """Deserialize a model instance from an RDF graph.

        This class method reconstructs a Pydantic model instance from RDF triples
        in a Graph. It extracts values for all fields annotated with RdfProperty
        by querying the graph for triples with the specified subject.

        Parameters
        ----------
        graph : Graph
            The rdflib Graph containing the RDF data.

        subject : URIRef | str
            The subject URI of the resource to deserialize. Can be a URIRef or
            a string that will be converted to a URIRef.

        base_uri : str | None, optional
            A base URI for converting the subject back to a relative identifier
            for the id field. If the subject starts with this base, the remainder
            is used as the id. Default is None.

        Returns
        -------
        RdfBaseModel
            A new instance of the model class populated with data from the graph.

        Raises
        ------
        ValidationError
            If the extracted values don't pass Pydantic validation.

        Examples
        --------
        Basic deserialization::

            graph = Graph()
            graph.parse(data=turtle_data, format="turtle")
            person = Person.from_rdf_graph(
                graph,
                URIRef("http://example.org/people/alice")
            )

        With base URI::

            person = Person.from_rdf_graph(
                graph,
                URIRef("http://example.org/people/alice"),
                base_uri="http://example.org/people/"
            )
            # person.id becomes "alice"

        Nested objects::

            # If the graph contains triples for both Person and Organization,
            # nested objects are automatically reconstructed
            person = Person.from_rdf_graph(graph, subject_uri)
            assert isinstance(person.org[0], Organization)

        Notes
        -----
        - Multi-valued properties are always returned as lists
        - Missing properties result in None values
        - Nested RdfBaseModel instances are recursively deserialized
        - Custom parsers in RdfProperty are applied during conversion
        - Type coercion follows Pydantic's validation rules

        See Also
        --------
        from_rdf : Deserialize from an RDF string
        to_rdf_graph : Serialize to a Graph
        """

        subject_uri = _ensure_uri(subject)
        if subject_uri is None:
            msg = "Subject URI cannot be None"
            raise ValueError(msg)
        values: dict[str, Any] = {}
        for name, field in cls.model_fields.items():
            prop = _get_rdf_property(field)
            if prop is None:
                continue
            predicate = prop.predicate_uri()
            is_list, accepts_scalar, inner_type = _field_type_info(field)

            # Check if the field supports dict aggregation (language maps)
            supports_dict = False
            annotation = _unwrap_annotation(field.annotation)
            origin = get_origin(annotation)
            if origin is Union or origin is types.UnionType:
                for arg in get_args(annotation):
                    arg_unwrapped = _unwrap_annotation(arg)
                    if get_origin(arg_unwrapped) is dict:
                        supports_dict = True
                        break

            objects = list(graph.objects(subject_uri, predicate))
            if not objects:
                continue
            model_type = _get_rdf_model_type(inner_type)
            if model_type:
                items: list[Any] = []
                for obj in objects:
                    if isinstance(obj, (URIRef, BNode)):
                        items.append(model_type.from_rdf_graph(graph, obj, base_uri=base_uri))
                    else:
                        items.append(_node_to_python(obj, inner_type, prop))
            elif get_origin(inner_type) is dict or (supports_dict and all(isinstance(obj, Literal) for obj in objects)):
                # Aggregate language-tagged literals into a dict
                res_dict: dict[str, Any] = {}

                for obj in objects:
                    if isinstance(obj, Literal):
                        lang = obj.language or ""
                        val: Any = obj.toPython()
                    else:
                        lang = ""
                        val = str(obj)

                    if lang in res_dict:
                        if not isinstance(res_dict[lang], list):
                            res_dict[lang] = [res_dict[lang]]
                        res_dict[lang].append(val)
                    else:
                        res_dict[lang] = val

                # If we aggregated into a dict but only have one key which is "" (untagged)
                # and the field supports a scalar (str or LangString), and we are in
                # a Union where we were "guessing" this should be a dict...
                if supports_dict and len(res_dict) == 1 and "" in res_dict:
                    # If the field also supports a list/scalar of strings, maybe we should unwrap
                    # But let's be careful: if the user explicitly typed it as a dict, they want a dict.
                    # LocalizedStr supports both.
                    # Heuristic: if it's a single untagged value, return the value directly
                    # so Pydantic uses the 'str' variant of the Union instead of 'dict'.
                    items = [res_dict[""]]
                    is_list = isinstance(res_dict[""], list)
                else:
                    items = [res_dict]
                    # For dicts, we treat it as a single item even if it has entries for multiple langs
                    is_list = False
            else:
                items = [_node_to_python(obj, inner_type, prop) for obj in objects]

            if is_list:
                # Return scalar when the field accepts both scalar and list
                # and exactly one value was found in the graph.
                if accepts_scalar and len(items) == 1:
                    values[name] = items[0]
                else:
                    values[name] = items
            else:
                values[name] = items[0]

        id_field = cls.rdf_id_field
        if id_field and id_field not in values:
            identifier = cls._identifier_from_subject(subject_uri, base_uri=base_uri)
            if identifier is not None:
                values[id_field] = identifier

        return cls(**values)

    @classmethod
    def from_rdf(
        cls: type[T],
        data: str | bytes,
        *,
        format: str = "turtle",
        subject: URIRef | str | None = None,
        base_uri: str | None = None,
    ) -> T:
        """Deserialize a model instance from an RDF string or bytes.

        This class method parses RDF data and reconstructs a Pydantic model instance.
        If the subject is not specified, it attempts to infer it from the graph
        (using rdf:type if available, or assuming a single subject).

        Parameters
        ----------
        data : str | bytes
            The RDF data as a string or bytes. Can be in any format supported
            by rdflib (Turtle, RDF/XML, JSON-LD, N-Triples, etc.).

        format : str, optional
            The RDF format of the input data. Common formats:
            - "turtle": Turtle/Trig format (default)
            - "xml": RDF/XML format
            - "json-ld": JSON-LD format
            - "nt" or "ntriples": N-Triples format
            - "n3": Notation3 format
            Default is "turtle".

        subject : URIRef | str | None, optional
            The subject URI to deserialize. If None, the subject is automatically
            inferred from the graph. Use this when the graph contains multiple
            resources. Default is None.

        base_uri : str | None, optional
            A base URI for generating relative identifiers. Default is None.

        Returns
        -------
        RdfBaseModel
            A new instance of the model class populated with the RDF data.

        Raises
        ------
        ValueError
            If subject is None and the subject cannot be inferred, or if multiple
            subjects are found and none is specified.
        ValidationError
            If the deserialized data doesn't pass Pydantic validation.

        Examples
        --------
        From Turtle string::

            turtle = '''
            @prefix foaf: <http://xmlns.com/foaf/0.1/> .

            foaf:alice a foaf:Person ;
                foaf:name "Alice Smith" ;
                foaf:mbox "alice@example.org" .
            '''
            person = Person.from_rdf(turtle, format="turtle")

        With explicit subject::

            person = Person.from_rdf(
                turtle_data,
                format="turtle",
                subject="http://example.org/people/alice"
            )

        From RDF/XML::

            person = Person.from_rdf(xml_data, format="xml")

        From JSON-LD::

            person = Person.from_rdf(jsonld_data, format="json-ld")

        Round-trip example::

            # Serialize
            original = Person(name=["Alice"])
            turtle = original.to_rdf("turtle")

            # Deserialize
            restored = Person.from_rdf(turtle)
            assert restored.name == original.name

        Notes
        -----
        - Subject inference works best with single-resource graphs
        - If rdf_type is set, it's used to find the subject
        - Format detection is not automatic; always specify the format
        - Bytes input is decoded as UTF-8

        See Also
        --------
        from_rdf_graph : Deserialize from a Graph object
        to_rdf : Serialize to an RDF string
        """

        graph = Graph()
        graph.parse(data=data, format=format)
        if subject is None:
            subject = cls._infer_subject(graph)
        if subject is None:
            raise ValueError("Unable to determine subject for RDF document; provide the subject explicitly.")
        return cls.from_rdf_graph(graph, subject, base_uri=base_uri)

    def _serialise_into_graph(
        self,
        graph: Graph,
        *,
        base_uri: str | None = None,
        rdf_uri_generator: Callable[[Any], URIRef | BNode] | None = None,
    ) -> URIRef | BNode:
        """Internal method to serialize this model into an RDF graph.

        Converts all annotated fields to RDF triples and adds them to the graph.
        This method handles the core serialization logic.

        Parameters
        ----------
        graph : Graph
            The rdflib Graph to add triples to.
        base_uri : str | None, optional
            Base URI for subject generation.
        rdf_uri_generator : Callable[[Any], Union[URIRef, BNode]] | None, optional
            A custom function to generate subject URIs for model instances.

        Returns
        -------
        URIRef | BNode
            The subject URI of the serialized resource.
        """
        subject = self._subject_uri(base_uri=base_uri, rdf_uri_generator=rdf_uri_generator)
        self._bind_prefixes(graph)

        rdf_type_uri = _ensure_uri(self.rdf_type)
        if rdf_type_uri is not None:
            graph.add((subject, RDF.type, rdf_type_uri))

        for name, field in self.__class__.model_fields.items():
            prop = _get_rdf_property(field)
            if prop is None:
                continue
            value = getattr(self, name)
            if value is None:
                continue
            predicate = prop.predicate_uri()
            is_list, _accepts_scalar, inner_type = _field_type_info(field)
            # Support both single values and lists for fields that allow both
            if is_list:
                values = value if isinstance(value, list) else [value]
            else:
                values = [value]
            for item in values:
                if item is None:
                    continue
                if isinstance(item, dict):
                    # Special handling for language maps in dicts
                    # We expect dict[str, str | list[str]]
                    for lang, val in item.items():
                        if isinstance(val, list):
                            for v in val:
                                graph.add((subject, predicate, Literal(v, lang=lang or None)))
                        else:
                            graph.add((subject, predicate, Literal(val, lang=lang or None)))
                    continue

                node = self._value_to_node(
                    item,
                    inner_type,
                    prop,
                    graph,
                    base_uri,
                    rdf_uri_generator=rdf_uri_generator,
                )
                graph.add((subject, predicate, node))

        return subject

    @classmethod
    def _identifier_from_subject(cls, subject: URIRef, *, base_uri: str | None = None) -> str | None:
        """Extract an identifier from a subject URI.

        Attempts to convert a subject URI back to a short identifier by removing
        the namespace or base URI prefix.

        Parameters
        ----------
        subject : URIRef
            The subject URI to convert.
        base_uri : str | None, optional
            Base URI to strip from the subject.

        Returns
        -------
        str | None
            The extracted identifier, or the full URI if no prefix matches.
        """
        subject_str = str(subject)
        namespace = cls._namespace_string()
        if namespace and subject_str.startswith(namespace):
            return subject_str[len(namespace) :]
        if base_uri:
            normalised = _normalise_base(base_uri)
            if subject_str.startswith(normalised):
                return subject_str[len(normalised) :]
        return subject_str

    @classmethod
    def _namespace_string(cls) -> str | None:
        """Get the namespace as a string.

        Returns
        -------
        str | None
            The namespace URI as a string, or None if no namespace is set.
        """
        namespace = cls.rdf_namespace
        if namespace is None:
            return None
        if isinstance(namespace, Namespace):
            return str(namespace)
        return str(namespace)

    def _subject_uri(
        self,
        *,
        base_uri: str | None = None,
        rdf_uri_generator: Callable[[Any], URIRef | BNode] | None = None,
    ) -> URIRef | BNode:
        """Generate the subject URI for this instance.

        Creates a URIRef for the RDF subject based on the id field, functionality,
        or generates a UUID if no identifier is available. If rdf_auto_uuid is False
        and no identifier is available, returns a BNode.

        Parameters
        ----------
        base_uri : str | None, optional
            Base URI for relative identifier resolution.
        rdf_uri_generator : Callable[[Any], Union[URIRef, BNode]] | None, optional
            A custom function to generate subject URIs for model instances.

        Returns
        -------
        URIRef | BNode
            The subject URI or Blank Node for this resource.
        """
        identifier: str | None = None
        if self.rdf_id_field:
            value = getattr(self, self.rdf_id_field, None)
            if value is not None:
                identifier = str(value)

        if identifier:
            if _looks_like_uri(identifier):
                return URIRef(identifier)
            namespace = self._namespace_string()
            if namespace:
                return URIRef(namespace + identifier)
            if base_uri:
                return URIRef(_normalise_base(base_uri) + identifier)
            return URIRef(identifier)

        # Check for custom URI generator
        generator = rdf_uri_generator if rdf_uri_generator is not None else self.rdf_uri_generator
        if generator is not None:
            # The generator takes the model instance as argument
            generated = generator(self)
            if generated is not None:
                return generated

        # If opted out of auto-UUIDs, return a blank node
        if not self.rdf_auto_uuid:
            return BNode()

        namespace = self._namespace_string()
        if namespace:
            return URIRef(namespace + str(uuid.uuid4()))
        return URIRef(f"urn:uuid:{uuid.uuid4()}")

    def _bind_prefixes(self, graph: Graph) -> None:
        """Bind namespace prefixes to the graph for readable serialization.

        Parameters
        ----------
        graph : Graph
            The graph to bind prefixes to.
        """
        prefixes = _default_prefixes()
        prefixes.update({key: str(value) for key, value in self.rdf_prefixes.items()})
        for prefix, namespace in prefixes.items():
            graph.bind(prefix, namespace)

    def _value_to_node(
        self,
        value: Any,
        expected_type: Any,
        prop: RdfProperty,
        graph: Graph,
        base_uri: str | None,
        *,
        rdf_uri_generator: Callable[[Any], URIRef | BNode] | None = None,
    ) -> URIRef | BNode | Literal:
        """Convert a Python value to an RDF node (URIRef, BNode, or Literal).

        Handles various Python types and converts them to appropriate RDF
        representations based on the field type and RdfProperty configuration.

        Parameters
        ----------
        value : Any
            The Python value to convert.
        expected_type : Any
            The expected type from the field annotation.
        prop : RdfProperty
            The RDF property metadata.
        graph : Graph
            The graph for nested object serialization.
        base_uri : str | None
            Base URI for nested objects.
        rdf_uri_generator : Callable[[Any], Union[URIRef, BNode]] | None, optional
            A custom function to generate subject URIs for model instances.

        Returns
        -------
        URIRef | BNode | Literal
            The RDF node representation of the value.
        """
        if prop.serializer is not None:
            value = prop.serializer(value)
        if isinstance(value, RdfBaseModel):
            return value._serialise_into_graph(graph, base_uri=base_uri, rdf_uri_generator=rdf_uri_generator)
        if isinstance(value, URIRef):
            return value
        if isinstance(value, Literal):
            return value
        if isinstance(value, Enum):
            value = value.value
        if isinstance(value, bytes):
            import base64

            encoded = base64.b64encode(value).decode("ascii")
            return Literal(encoded, datatype=XSD.base64Binary)
        if isinstance(value, LangString):
            return Literal(value.value, lang=value.lang)

        if isinstance(value, (datetime, date, time, int, float, bool, Decimal, uuid.UUID)):
            datatype = prop.datatype_uri()
            if datatype is None:
                datatype = _python_datatype(value)
            return Literal(value, datatype=datatype)
        if isinstance(value, str):
            datatype = prop.datatype_uri()
            if prop.language:
                return Literal(value, lang=prop.language)
            if datatype is not None:
                return Literal(value, datatype=datatype)

            # Check if URIRef is an expected type
            origin = get_origin(expected_type)
            is_union = origin is Union or (hasattr(types, "UnionType") and origin is types.UnionType)
            if is_union:
                allowed_types = get_args(expected_type)
            else:
                allowed_types = (expected_type,)

            if URIRef in allowed_types and _looks_like_uri(value):
                return URIRef(value)
            return Literal(value)
        return Literal(value)

    @classmethod
    def _infer_subject(cls, graph: Graph) -> URIRef | None:
        """Infer the subject URI from a graph.

        Attempts to determine which subject in the graph corresponds to this
        model type, using rdf:type if available or assuming a single subject.

        Parameters
        ----------
        graph : Graph
            The graph to analyze.

        Returns
        -------
        URIRef | None
            The inferred subject URI, or None if it cannot be determined.

        Raises
        ------
        ValueError
            If multiple subjects are found and cannot be disambiguated.
        """
        rdf_type_uri = _ensure_uri(cls.rdf_type)
        if rdf_type_uri is not None:
            subjects = _unique(graph.subjects(RDF.type, rdf_type_uri))
            if not subjects:
                return None
            if len(subjects) > 1:
                raise ValueError(
                    "Multiple resources of the requested rdf:type were found; provide the subject explicitly."
                )
            return subjects[0]  # type: ignore[no-any-return]
        subjects = _unique(graph.subjects())
        if not subjects:
            return None
        if len(subjects) > 1:
            raise ValueError("Multiple resources found in graph; provide the subject explicitly.")
        return subjects[0]  # type: ignore[no-any-return]


def _get_rdf_property(field: Any) -> RdfProperty | None:
    """Extract RdfProperty metadata from a field's metadata or annotation.

    Parameters
    ----------
    field : Any
        A Pydantic field information object.

    Returns
    -------
    RdfProperty | None
        The RdfProperty if found in metadata, otherwise None.
    """
    metadata = getattr(field, "metadata", ()) or ()
    for item in metadata:
        if isinstance(item, RdfProperty):
            return item
    annotation = getattr(field, "annotation", None)
    if annotation is not None:
        for item in _annotation_metadata(annotation):
            if isinstance(item, RdfProperty):
                return item
    return None


def _field_type_info(field: Any) -> tuple[bool, bool, Any]:
    """Determine if a field is a list type and extract its inner type.

    Also handles Optional types by unwrapping Union[T, None].

    Parameters
    ----------
    field : Any
        A Pydantic field information object.

    Returns
    -------
    tuple[bool, bool, Any]
        A tuple of (is_list, accepts_scalar, inner_type).
        - is_list is True if the field accepts list values.
        - accepts_scalar is True if the field also accepts a single
          (non-list) value, e.g. ``str | list[str] | None``.
        - inner_type is the type of individual elements.
    """
    annotation = getattr(field, "annotation", Any)
    annotation = _unwrap_annotation(annotation)

    origin = get_origin(annotation)
    # Handle both Union[T, None], T | None syntax and Union with list
    if origin is Union or origin is types.UnionType:
        args = get_args(annotation)
        # Check if any arg is a list to support Union[str, list[str]]
        has_list = False
        list_item_type: Any = Any
        non_none_non_list_args: list[Any] = []
        for arg in args:
            arg_unwrapped = _unwrap_annotation(arg)
            if get_origin(arg_unwrapped) is list:
                has_list = True
                list_args = get_args(arg_unwrapped)
                list_item_type = _unwrap_annotation(list_args[0]) if list_args else Any
            elif arg is not type(None):
                non_none_non_list_args.append(arg)

        if has_list:
            # The field has a list variant. If it also has non-None scalar
            # type args, it accepts scalars too (e.g. str | list[str] | None).
            accepts_scalar = len(non_none_non_list_args) > 0
            return True, accepts_scalar, list_item_type

        # Existing logic for unwrapping Optional[T]
        non_none_args = [arg for arg in args if arg is not type(None)]
        if len(non_none_args) == 1:
            annotation = _unwrap_annotation(non_none_args[0])
            origin = get_origin(annotation)

    if origin is list:
        item_type = _unwrap_annotation(get_args(annotation)[0])
        return True, False, item_type

    return False, False, annotation


def _unwrap_annotation(annotation: Any) -> Any:
    """Unwrap Annotated type to get the actual type.

    Recursively unwraps until reaching a non-Annotated type.

    Parameters
    ----------
    annotation : Any
        A potentially Annotated type hint.

    Returns
    -------
    Any
        The unwrapped type, or the original if not Annotated.
    """
    while True:
        origin = get_origin(annotation)
        if origin is None:
            return annotation
        if origin is Annotated:
            annotation = get_args(annotation)[0]
            continue
        return annotation


def _annotation_metadata(annotation: Any) -> tuple[Any, ...]:
    """Extract metadata from an Annotated type.

    Parameters
    ----------
    annotation : Any
        A type annotation, possibly Annotated.

    Returns
    -------
    tuple[Any, ...]
        The metadata items if Annotated, otherwise empty tuple.
    """
    if get_origin(annotation) is Annotated:
        args = get_args(annotation)
        return tuple(args[1:])
    return ()


def _node_to_python(node: Any, expected_type: Any, prop: RdfProperty) -> Any:
    """Convert an RDF node to a Python value.

    Handles deserialization of URIRef and Literal nodes to appropriate Python
    types based on field type hints and RdfProperty configuration.

    Parameters
    ----------
    node : Any
        The RDF node to convert (URIRef or Literal).
    expected_type : Any
        The expected Python type from field annotations.
    prop : RdfProperty
        The RDF property metadata.

    Returns
    -------
    Any
        The converted Python value.

    Raises
    ------
    TypeError
        If a nested RDF model is encountered (should be handled separately).
    """
    if prop.parser is not None:
        return prop.parser(node)

    if expected_type is LangString or (isinstance(expected_type, type) and issubclass(expected_type, LangString)):
        if isinstance(node, Literal):
            return LangString(value=str(node), lang=node.language)
        return LangString(value=str(node))

    if _is_rdf_model(expected_type):
        raise TypeError("Nested RDF models should be handled separately.")

    if expected_type is URIRef:
        if isinstance(node, URIRef):
            return node
        return URIRef(str(node))

    if isinstance(node, Literal):
        value = node.toPython()
    else:
        value = str(node)

    if expected_type is Any or expected_type is None:
        return value

    if expected_type is str:
        return str(value)

    if expected_type in {int, float, bool}:
        try:
            return expected_type(value)
        except (TypeError, ValueError):
            return value

    if expected_type is datetime:
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(str(value))
        except ValueError:
            return value

    if expected_type is date:
        if isinstance(value, date):
            return value
        try:
            return date.fromisoformat(str(value))
        except ValueError:
            return value

    if expected_type is time:
        if isinstance(value, time):
            return value
        try:
            return time.fromisoformat(str(value))
        except ValueError:
            return value

    if expected_type is Decimal:
        try:
            return Decimal(value)
        except (ValueError, TypeError, ArithmeticError):
            return value

    if expected_type is bytes:
        if isinstance(value, bytes):
            return value
        # rdflib handles base64 decoding for XSD.base64Binary
        return value

    if expected_type is uuid.UUID:
        if isinstance(value, uuid.UUID):
            return value
        try:
            return uuid.UUID(str(value))
        except (ValueError, TypeError):
            return value

    if isinstance(expected_type, type) and issubclass(expected_type, Enum):
        return expected_type(value)

    return value


def _python_datatype(value: Any) -> URIRef | None:
    """Infer XSD datatype URI from a Python value.

    Parameters
    ----------
    value : Any
        A Python value to determine the datatype for.

    Returns
    -------
    URIRef | None
        The XSD datatype URI, or None if no mapping exists.
    """
    if isinstance(value, bool):
        return XSD.boolean
    if isinstance(value, int):
        return XSD.integer
    if isinstance(value, float):
        return XSD.double
    if isinstance(value, datetime):
        return XSD.dateTime
    if isinstance(value, date):
        return XSD.date
    if isinstance(value, time):
        return XSD.time
    if isinstance(value, Decimal):
        return XSD.decimal
    if isinstance(value, bytes):
        return XSD.base64Binary
    if isinstance(value, uuid.UUID):
        return XSD.string
    return None


def _ensure_uri(value: str | URIRef | Namespace | None) -> URIRef | None:
    """Convert various types to a URIRef.

    Parameters
    ----------
    value : str | URIRef | Namespace | None
        A value that might represent a URI.

    Returns
    -------
    URIRef | None
        The URIRef representation, or None if the value is None.
    """
    if value is None:
        return None
    if isinstance(value, URIRef):
        return value
    if isinstance(value, Namespace):
        return URIRef(str(value))
    return URIRef(str(value))


URI_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def _looks_like_uri(value: str) -> bool:
    """Check if a string looks like a URI using a URI scheme pattern.

    Parameters
    ----------
    value : str
        A string to check.

    Returns
    -------
    bool
        True if the string starts with a URI scheme (e.g., 'http:', 'urn:').
    """
    return bool(URI_PATTERN.match(value))


def _normalise_base(base_uri: str) -> str:
    """Normalize a base URI to ensure it ends with '/' or '#'.

    Parameters
    ----------
    base_uri : str
        A base URI string.

    Returns
    -------
    str
        The normalized base URI.
    """
    if base_uri.endswith(("/", "#")):
        return base_uri
    return base_uri + "/"


def _unique(values: Iterable[Any]) -> list[Any]:
    """Return unique items from an iterable, preserving order.

    Parameters
    ----------
    values : Iterable[Any]
        An iterable of items.

    Returns
    -------
    list[Any]
        A list with duplicates removed, in original order.
    """
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _default_prefixes() -> dict[str, str]:
    """Get the default namespace prefixes for RDF serialization.

    Returns
    -------
    dict[str, str]
        A dictionary mapping prefix strings to namespace URI strings.
        Includes rdf and xsd by default.
    """
    return {"rdf": str(RDF), "xsd": str(XSD)}


def _is_rdf_model(value: Any) -> bool:
    """Check if a value is an RdfBaseModel subclass.

    Parameters
    ----------
    value : Any
        A value to check (typically a type).

    Returns
    -------
    bool
        True if value is a class and a subclass of RdfBaseModel.
    """
    return isinstance(value, type) and issubclass(value, RdfBaseModel)


def _get_rdf_model_type(type_hint: Any) -> type[RdfBaseModel] | None:
    """Get the RdfBaseModel type from a type hint (possibly a Union).

    Parameters
    ----------
    type_hint : Any
        The type hint to check.

    Returns
    -------
    Type[RdfBaseModel] | None
        The RdfBaseModel subclass if found, otherwise None.
    """
    if _is_rdf_model(type_hint):
        return type_hint  # type: ignore[no-any-return]

    origin = get_origin(type_hint)
    if origin is Union or (hasattr(types, "UnionType") and origin is types.UnionType):
        for arg in get_args(type_hint):
            if _is_rdf_model(arg):
                return arg  # type: ignore[no-any-return]
    return None


__all__ = ["RdfBaseModel", "RdfProperty", "LangString", "LocalizedStr"]

# Ensure defaults are preserved when using lightweight pydantic substitutes.
RdfBaseModel.rdf_id_field = "id"
