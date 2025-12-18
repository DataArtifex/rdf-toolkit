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

from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
import re
from typing import Any, ClassVar, Dict, Iterable, Optional, Tuple, Type, TypeVar, Union, get_args, get_origin, Annotated
import uuid

from pydantic import BaseModel, ConfigDict, Field
from rdflib import Graph, Literal, Namespace, RDF, URIRef, XSD, BNode
from typing import Callable

T = TypeVar("T", bound="RdfBaseModel")


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

    predicate: Union[str, URIRef]
    datatype: Union[str, URIRef, None] = None
    language: Optional[str] = None
    serializer: Optional[Any] = None
    parser: Optional[Any] = None

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
        return _ensure_uri(self.predicate)

    def datatype_uri(self) -> Optional[URIRef]:
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

    rdf_type: ClassVar[Union[str, URIRef, None]] = None
    rdf_namespace: ClassVar[Union[str, Namespace, None]] = None
    rdf_id_field: ClassVar[Optional[str]] = "id"
    rdf_prefixes: ClassVar[Dict[str, Union[str, Namespace]]] = {}
    
    rdf_auto_uuid: bool = Field(default=True, exclude=True)
    rdf_uri_generator: Optional[Callable[[Any], Union[URIRef, BNode]]] = Field(default=None, exclude=True)

    def to_rdf_graph(
        self,
        graph: Optional[Graph] = None,
        *,
        base_uri: Optional[str] = None,
        rdf_uri_generator: Optional[Callable[[Any], Union[URIRef, BNode]]] = None
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
        base_uri: Optional[str] = None,
        rdf_uri_generator: Optional[Callable[[Any], Union[URIRef, BNode]]] = None,
        **kwargs: Any
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
        return graph.serialize(format=format, **kwargs)

    @classmethod
    def from_rdf_graph(
        cls: Type[T], graph: Graph, subject: Union[URIRef, str], *, base_uri: Optional[str] = None
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
        values: Dict[str, Any] = {}
        for name, field in cls.model_fields.items():
            prop = _get_rdf_property(field)
            if prop is None:
                continue
            predicate = prop.predicate_uri()
            is_list, inner_type = _field_type_info(field)
            objects = list(graph.objects(subject_uri, predicate))
            if not objects:
                continue
            model_type = _get_rdf_model_type(inner_type)
            if model_type:
                items = []
                for obj in objects:
                    if isinstance(obj, (URIRef, BNode)):
                        items.append(model_type.from_rdf_graph(graph, obj, base_uri=base_uri))
                    else:
                        items.append(_node_to_python(obj, inner_type, prop))
            else:
                items = [_node_to_python(obj, inner_type, prop) for obj in objects]
            values[name] = items if is_list else items[0]

        id_field = cls.rdf_id_field
        if id_field and id_field not in values:
            identifier = cls._identifier_from_subject(subject_uri, base_uri=base_uri)
            if identifier is not None:
                values[id_field] = identifier

        return cls(**values)

    @classmethod
    def from_rdf(
        cls: Type[T], data: Union[str, bytes], *, format: str = "turtle", subject: Union[URIRef, str, None] = None,
        base_uri: Optional[str] = None
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
        base_uri: Optional[str] = None,
        rdf_uri_generator: Optional[Callable[[Any], Union[URIRef, BNode]]] = None
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

        for name, field in self.model_fields.items():
            prop = _get_rdf_property(field)
            if prop is None:
                continue
            value = getattr(self, name)
            if value is None:
                continue
            predicate = prop.predicate_uri()
            is_list, inner_type = _field_type_info(field)
            values = value if is_list else [value]
            for item in values:
                if item is None:
                    continue
                node = self._value_to_node(item, inner_type, prop, graph, base_uri, rdf_uri_generator=rdf_uri_generator)
                graph.add((subject, predicate, node))

        return subject

    @classmethod
    def _identifier_from_subject(cls, subject: URIRef, *, base_uri: Optional[str] = None) -> Optional[str]:
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
            return subject_str[len(namespace):]
        if base_uri:
            normalised = _normalise_base(base_uri)
            if subject_str.startswith(normalised):
                return subject_str[len(normalised):]
        return subject_str

    @classmethod
    def _namespace_string(cls) -> Optional[str]:
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
        base_uri: Optional[str] = None,
        rdf_uri_generator: Optional[Callable[[Any], Union[URIRef, BNode]]] = None
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
        identifier: Optional[str] = None
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
        base_uri: Optional[str],
        *,
        rdf_uri_generator: Optional[Callable[[Any], Union[URIRef, BNode]]] = None
    ) -> URIRef | Literal:
        """Convert a Python value to an RDF node (URIRef or Literal).
        
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
        URIRef | Literal
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
            encoded = base64.b64encode(value).decode('ascii')
            return Literal(encoded, datatype=XSD.base64Binary)
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
            if expected_type is URIRef and _looks_like_uri(value):
                return URIRef(value)
            return Literal(value)
        return Literal(value)

    @classmethod
    def _infer_subject(cls, graph: Graph) -> Optional[URIRef]:
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
            return subjects[0]
        subjects = _unique(graph.subjects())
        if not subjects:
            return None
        if len(subjects) > 1:
            raise ValueError("Multiple resources found in graph; provide the subject explicitly.")
        return subjects[0]


def _get_rdf_property(field: Any) -> Optional[RdfProperty]:
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


def _field_type_info(field: Any) -> Tuple[bool, Any]:
    """Determine if a field is a list type and extract its inner type.
    
    Also handles Optional types by unwrapping Union[T, None].
    
    Parameters
    ----------
    field : Any
        A Pydantic field information object.
    
    Returns
    -------
    tuple[bool, Any]
        A tuple of (is_list, inner_type). is_list is True if the field accepts
        multiple values, inner_type is the type of individual elements.
    """
    annotation = getattr(field, "annotation", Any)
    annotation = _unwrap_annotation(annotation)

    origin = get_origin(annotation)
    if origin is Union:
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if len(args) == 1:
            annotation = _unwrap_annotation(args[0])
            origin = get_origin(annotation)

    if origin is list:
        item_type = _unwrap_annotation(get_args(annotation)[0])
        return True, item_type

    return False, annotation


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


def _annotation_metadata(annotation: Any) -> Tuple[Any, ...]:
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


def _python_datatype(value: Any) -> Optional[URIRef]:
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


def _ensure_uri(value: Union[str, URIRef, Namespace, None]) -> Optional[URIRef]:
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
    if base_uri.endswith(('/', '#')):
        return base_uri
    return base_uri + '/'


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


def _default_prefixes() -> Dict[str, str]:
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


def _get_rdf_model_type(type_hint: Any) -> Optional[Type[RdfBaseModel]]:
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
        return type_hint
    
    origin = get_origin(type_hint)
    if origin is Union:
        for arg in get_args(type_hint):
            if _is_rdf_model(arg):
                return arg
    return None



__all__ = ["RdfBaseModel", "RdfProperty"]

# Ensure defaults are preserved when using lightweight pydantic substitutes.
RdfBaseModel.rdf_id_field = "id"

