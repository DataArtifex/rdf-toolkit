"""Utilities to map Pydantic models to RDF graphs using field annotations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
import re
from typing import Any, ClassVar, Dict, Iterable, Optional, Tuple, Type, TypeVar, Union, get_args, get_origin, Annotated
import uuid

from pydantic import BaseModel, ConfigDict
from rdflib import Graph, Literal, Namespace, RDF, URIRef, XSD

T = TypeVar("T", bound="RdfBaseModel")


@dataclass(frozen=True)
class RdfProperty:
    """Metadata used to describe how a Pydantic field maps to RDF."""

    predicate: Union[str, URIRef]
    datatype: Union[str, URIRef, None] = None
    language: Optional[str] = None
    serializer: Optional[Any] = None
    parser: Optional[Any] = None

    def predicate_uri(self) -> URIRef:
        return _ensure_uri(self.predicate)

    def datatype_uri(self) -> Optional[URIRef]:
        return _ensure_uri(self.datatype)


class RdfBaseModel(BaseModel):
    """Base class providing RDF serialisation for Pydantic models."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    rdf_type: ClassVar[Union[str, URIRef, None]] = None
    rdf_namespace: ClassVar[Union[str, Namespace, None]] = None
    rdf_id_field: ClassVar[Optional[str]] = "id"
    rdf_prefixes: ClassVar[Dict[str, Union[str, Namespace]]] = {}

    def to_rdf_graph(self, graph: Optional[Graph] = None, *, base_uri: Optional[str] = None) -> Graph:
        """Serialise the model into an :class:`rdflib.Graph`."""

        graph = graph if graph is not None else Graph()
        self._serialise_into_graph(graph, base_uri=base_uri)
        return graph

    def to_rdf(self, format: str = "turtle", *, base_uri: Optional[str] = None, **kwargs: Any) -> str:
        """Serialise the model directly into a string representation."""

        graph = self.to_rdf_graph(base_uri=base_uri)
        return graph.serialize(format=format, **kwargs)

    @classmethod
    def from_rdf_graph(
        cls: Type[T], graph: Graph, subject: Union[URIRef, str], *, base_uri: Optional[str] = None
    ) -> T:
        """Recreate a model instance from an RDF graph and subject."""

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
            if _is_rdf_model(inner_type):
                items = [inner_type.from_rdf_graph(graph, obj, base_uri=base_uri) for obj in objects]
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
        """Recreate a model from a serialised RDF document."""

        graph = Graph()
        graph.parse(data=data, format=format)
        if subject is None:
            subject = cls._infer_subject(graph)
        if subject is None:
            raise ValueError("Unable to determine subject for RDF document; provide the subject explicitly.")
        return cls.from_rdf_graph(graph, subject, base_uri=base_uri)

    def _serialise_into_graph(self, graph: Graph, *, base_uri: Optional[str] = None) -> URIRef:
        subject = self._subject_uri(base_uri=base_uri)
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
                node = self._value_to_node(item, inner_type, prop, graph, base_uri)
                graph.add((subject, predicate, node))

        return subject

    @classmethod
    def _identifier_from_subject(cls, subject: URIRef, *, base_uri: Optional[str] = None) -> Optional[str]:
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
        namespace = cls.rdf_namespace
        if namespace is None:
            return None
        if isinstance(namespace, Namespace):
            return str(namespace)
        return str(namespace)

    def _subject_uri(self, *, base_uri: Optional[str] = None) -> URIRef:
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

        namespace = self._namespace_string()
        if namespace:
            return URIRef(namespace + str(uuid.uuid4()))
        return URIRef(f"urn:uuid:{uuid.uuid4()}")

    def _bind_prefixes(self, graph: Graph) -> None:
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
    ) -> URIRef | Literal:
        if prop.serializer is not None:
            value = prop.serializer(value)
        if isinstance(value, RdfBaseModel):
            return value._serialise_into_graph(graph, base_uri=base_uri)
        if isinstance(value, URIRef):
            return value
        if isinstance(value, Literal):
            return value
        if isinstance(value, Enum):
            value = value.value
        if isinstance(value, (datetime, date, time, int, float, bool, Decimal)):
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
    while True:
        origin = get_origin(annotation)
        if origin is None:
            return annotation
        if origin is Annotated:
            annotation = get_args(annotation)[0]
            continue
        return annotation


def _annotation_metadata(annotation: Any) -> Tuple[Any, ...]:
    if get_origin(annotation) is Annotated:
        args = get_args(annotation)
        return tuple(args[1:])
    return ()


def _node_to_python(node: Any, expected_type: Any, prop: RdfProperty) -> Any:
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
        except Exception:  # pragma: no cover - fallback path
            return value
    if isinstance(expected_type, type) and issubclass(expected_type, Enum):
        return expected_type(value)
    return value


def _python_datatype(value: Any) -> Optional[URIRef]:
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
    return None


def _ensure_uri(value: Union[str, URIRef, Namespace, None]) -> Optional[URIRef]:
    if value is None:
        return None
    if isinstance(value, URIRef):
        return value
    if isinstance(value, Namespace):
        return URIRef(str(value))
    return URIRef(str(value))


URI_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def _looks_like_uri(value: str) -> bool:
    return bool(URI_PATTERN.match(value))


def _normalise_base(base_uri: str) -> str:
    if base_uri.endswith(('/', '#')):
        return base_uri
    return base_uri + '/'


def _unique(values: Iterable[Any]) -> list[Any]:
    seen = []
    for value in values:
        if value not in seen:
            seen.append(value)
    return seen


def _default_prefixes() -> Dict[str, str]:
    return {"rdf": str(RDF), "xsd": str(XSD)}


def _is_rdf_model(value: Any) -> bool:
    return isinstance(value, type) and issubclass(value, RdfBaseModel)


__all__ = ["RdfBaseModel", "RdfProperty"]

# Ensure defaults are preserved when using lightweight pydantic substitutes.
RdfBaseModel.rdf_id_field = "id"

