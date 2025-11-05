"""A lightweight subset of :mod:`rdflib` for unit testing without external dependencies."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple


class URIRef(str):
    """Represents a URI reference."""


@dataclass(frozen=True)
class Literal:
    """Represents an RDF literal value."""

    value: Any
    datatype: Optional[URIRef] = None
    lang: Optional[str] = None

    def toPython(self) -> Any:
        if self.datatype == XSD.boolean:
            if isinstance(self.value, bool):
                return self.value
            return str(self.value).lower() in {"true", "1"}
        if self.datatype == XSD.integer:
            try:
                return int(self.value)
            except Exception:
                return self.value
        if self.datatype in {XSD.float, XSD.double, XSD.decimal}:
            try:
                return float(self.value)
            except Exception:
                return self.value
        if self.datatype == XSD.dateTime and isinstance(self.value, str):
            try:
                return datetime.fromisoformat(self.value)
            except ValueError:
                return self.value
        if self.datatype == XSD.date and isinstance(self.value, str):
            try:
                return date.fromisoformat(self.value)
            except ValueError:
                return self.value
        if self.datatype == XSD.time and isinstance(self.value, str):
            try:
                return time.fromisoformat(self.value)
            except ValueError:
                return self.value
        return self.value

    def __hash__(self) -> int:  # pragma: no cover - dataclass default is not stable enough for set membership
        return hash((self.value, self.datatype, self.lang))


class Namespace(str):
    """Simplified namespace implementation."""

    def __new__(cls, uri: str):
        return str.__new__(cls, uri)

    def __getattr__(self, name: str) -> URIRef:
        if name.startswith("__"):
            raise AttributeError(name)
        return URIRef(self + name)

    def __getitem__(self, name: str) -> URIRef:
        return URIRef(self + name)


class NamespaceManager:
    def __init__(self) -> None:
        self._namespaces: Dict[str, str] = {}

    def bind(self, prefix: str, namespace: str) -> None:
        self._namespaces[prefix] = namespace

    def qname(self, uri: URIRef) -> str:
        uri_str = str(uri)
        for prefix, namespace in self._namespaces.items():
            if uri_str.startswith(namespace):
                return f"{prefix}:{uri_str[len(namespace):]}"
        return uri_str


class Graph:
    """Simplified in-memory triple store."""

    def __init__(self) -> None:
        self._triples: set[Tuple[Any, Any, Any]] = set()
        self._namespaces: Dict[str, str] = {}
        self.namespace_manager = NamespaceManager()

    def add(self, triple: Tuple[Any, Any, Any]) -> None:
        self._triples.add(triple)

    def __contains__(self, triple: Tuple[Any, Any, Any]) -> bool:
        return triple in self._triples

    def bind(self, prefix: str, namespace: str) -> None:
        namespace_str = str(namespace)
        self._namespaces[prefix] = namespace_str
        self.namespace_manager.bind(prefix, namespace_str)

    def objects(self, subject: Any | None = None, predicate: Any | None = None) -> Iterator[Any]:
        for s, p, o in self._triples:
            if subject is not None and s != subject:
                continue
            if predicate is not None and p != predicate:
                continue
            yield o

    def subjects(self, predicate: Any | None = None, object: Any | None = None) -> Iterator[Any]:
        for s, p, o in self._triples:
            if predicate is not None and p != predicate:
                continue
            if object is not None and o != object:
                continue
            yield s

    def value(self, subject: Any, predicate: Any, default: Any | None = None) -> Any:
        for obj in self.objects(subject, predicate):
            return obj
        return default

    def serialize(self, format: str = "turtle", **_: Any) -> str:
        if format == "turtle":
            return _serialize_turtle(self)
        if format in {"xml", "rdfxml"}:
            return _serialize_xml(self)
        raise ValueError(f"Unsupported format: {format}")

    def parse(self, data: str, format: str = "turtle", **_: Any) -> "Graph":
        if format != "turtle":
            raise ValueError("Only Turtle input is supported by this lightweight implementation")
        _parse_turtle(self, data)
        return self

    def query(self, query: str) -> Iterable[Any]:
        normalized = " ".join(query.lower().split())
        if "select (count(*) as ?n" in normalized:
            yield _Result(n=len(self._triples))
            return
        if "select ?type (count(?instance) as ?n" in normalized:
            counts: Dict[Any, int] = {}
            for s, p, o in self._triples:
                if p == RDF.type:
                    counts[o] = counts.get(o, 0) + 1
            for rdf_type, count in sorted(counts.items(), key=lambda item: str(item[0])):
                yield _Result(type=rdf_type, n=count)
            return
        if "select ?property (count(?property) as ?n" in normalized:
            counts = {}
            typed_subjects = {s for s, p, _ in self._triples if p == RDF.type}
            for s, p, _ in self._triples:
                if s in typed_subjects:
                    counts[p] = counts.get(p, 0) + 1
            for predicate, count in sorted(counts.items(), key=lambda item: str(item[0])):
                yield _Result(property=predicate, n=count)
            return
        raise NotImplementedError("SPARQL querying is not supported in this lightweight implementation")

    def triples(self) -> Iterable[Tuple[Any, Any, Any]]:
        return iter(self._triples)


class Collection:
    def __init__(self, graph: Graph, head: URIRef, values: Iterable[Any]):
        self.graph = graph
        self.head = head
        self.values = list(values)
        self._build()

    def _build(self) -> None:
        if not self.values:
            self.graph.add((self.head, RDF.first, RDF.nil))
            self.graph.add((self.head, RDF.rest, RDF.nil))
            return
        current = self.head
        for index, value in enumerate(self.values):
            self.graph.add((current, RDF.first, value))
            if index == len(self.values) - 1:
                self.graph.add((current, RDF.rest, RDF.nil))
            else:
                next_node = URIRef(f"{self.head}_rest{index}")
                self.graph.add((current, RDF.rest, next_node))
                current = next_node


def _serialize_turtle(graph: Graph) -> str:
    lines: List[str] = []
    for prefix, namespace in sorted(graph._namespaces.items()):
        lines.append(f"@prefix {prefix}: <{namespace}> .")
    if graph._triples:
        lines.append("")
    for subject, predicate, obj in sorted(graph._triples, key=_triple_sort_key):
        lines.append(f"{_format_term(subject)} {_format_term(predicate)} {_format_term(obj)} .")
    return "\n".join(lines) + "\n"


def _serialize_xml(graph: Graph) -> str:
    namespaces = {"rdf": str(RDF), "xsd": str(XSD)}
    namespaces.update(graph._namespaces)
    attrs = " ".join(f'xmlns:{prefix}="{uri}"' for prefix, uri in sorted(namespaces.items()))
    lines = [f"<rdf:RDF {attrs}>"]
    for subject, predicate, obj in sorted(graph._triples, key=_triple_sort_key):
        lines.append(f"  <rdf:Description rdf:about=\"{_escape(str(subject))}\">")
        pred_uri = str(predicate)
        local_name = _local_name(pred_uri)
        if isinstance(obj, Literal):
            if obj.lang:
                lines.append(
                    f"    <{local_name} xml:lang=\"{obj.lang}\">{_escape(str(obj.value))}</{local_name}>"
                )
            elif obj.datatype:
                lines.append(
                    f"    <{local_name} rdf:datatype=\"{obj.datatype}\">{_escape(str(obj.value))}</{local_name}>"
                )
            else:
                lines.append(f"    <{local_name}>{_escape(str(obj.value))}</{local_name}>")
        else:
            lines.append(
                f"    <{local_name} rdf:resource=\"{_escape(str(obj))}\" />"
            )
        lines.append("  </rdf:Description>")
    lines.append("</rdf:RDF>")
    return "\n".join(lines)


def _parse_turtle(graph: Graph, data: str) -> None:
    for raw_line in data.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("@prefix"):
            prefix, namespace = _parse_prefix(line)
            graph.bind(prefix, namespace)
            continue
        if not line.endswith("."):
            continue
        body = line[:-1].strip()
        subject, predicate, obj = _split_triple(body)
        graph.add((
            _parse_term(graph, subject),
            _parse_term(graph, predicate),
            _parse_object(graph, obj),
        ))


def _parse_prefix(line: str) -> Tuple[str, str]:
    _, rest = line.split("@prefix", 1)
    prefix, uri_part = rest.strip().split(":", 1)
    uri = uri_part.strip()
    if uri.endswith("."):
        uri = uri[:-1].strip()
    if not (uri.startswith("<") and uri.endswith(">")):
        raise ValueError(f"Invalid prefix declaration: {line}")
    return prefix.strip(), uri[1:-1]


def _split_triple(line: str) -> Tuple[str, str, str]:
    tokens: List[str] = []
    current: List[str] = []
    in_quote = False
    escape = False
    for char in line:
        if in_quote:
            current.append(char)
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_quote = False
        else:
            if char == '"':
                in_quote = True
                current.append(char)
            elif char in {" ", "\t"}:
                if current:
                    tokens.append("".join(current))
                    current = []
            else:
                current.append(char)
    if current:
        tokens.append("".join(current))
    if len(tokens) < 3:
        raise ValueError(f"Unable to parse triple from line: {line}")
    subject = tokens[0]
    predicate = tokens[1]
    obj = " ".join(tokens[2:])
    return subject, predicate, obj


def _parse_term(graph: Graph, token: str) -> Any:
    if token.startswith("<") and token.endswith(">"):
        return URIRef(token[1:-1])
    if token == "a":
        return RDF.type
    if ":" in token:
        prefix, local = token.split(":", 1)
        namespace = graph._namespaces.get(prefix)
        if namespace is None:
            raise ValueError(f"Unknown prefix {prefix}")
        return URIRef(namespace + local)
    return URIRef(token)


def _parse_object(graph: Graph, token: str) -> Any:
    token = token.strip()
    if token.startswith('"'):
        value, rest = _split_literal(token)
        lang = None
        datatype = None
        if rest.startswith("@"):
            lang = rest[1:]
        elif rest.startswith("^^"):
            datatype_token = rest[2:]
            datatype = _parse_term(graph, datatype_token)
        return Literal(value, datatype=datatype, lang=lang)
    return _parse_term(graph, token)


def _split_literal(token: str) -> Tuple[str, str]:
    end = 1
    escaped = False
    while end < len(token):
        char = token[end]
        if char == "\\" and not escaped:
            escaped = True
            end += 1
            continue
        if char == '"' and not escaped:
            break
        escaped = False
        end += 1
    value = token[1:end]
    rest = token[end + 1 :].strip()
    return value, rest


def _format_term(term: Any) -> str:
    if isinstance(term, URIRef):
        return f"<{term}>"
    if isinstance(term, Literal):
        literal = f'"{term.value}"'
        if term.lang:
            literal += f"@{term.lang}"
        elif term.datatype:
            literal += f"^^<{term.datatype}>"
        return literal
    return str(term)


def _triple_sort_key(triple: Tuple[Any, Any, Any]) -> Tuple[str, str, str]:
    s, p, o = triple
    return (str(s), str(p), str(o))


def _escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _local_name(uri: str) -> str:
    for sep in ("#", "/"):
        if sep in uri:
            return uri.rsplit(sep, 1)[-1]
    return uri


class _Result:
    def __init__(self, **entries: Any) -> None:
        self.__dict__.update(entries)


RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
RDF.type = URIRef(str(RDF) + "type")
RDF.first = URIRef(str(RDF) + "first")
RDF.rest = URIRef(str(RDF) + "rest")
RDF.nil = URIRef(str(RDF) + "nil")

XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
XSD.string = URIRef(str(XSD) + "string")
XSD.boolean = URIRef(str(XSD) + "boolean")
XSD.integer = URIRef(str(XSD) + "integer")
XSD.float = URIRef(str(XSD) + "float")
XSD.double = URIRef(str(XSD) + "double")
XSD.decimal = URIRef(str(XSD) + "decimal")
XSD.date = URIRef(str(XSD) + "date")
XSD.dateTime = URIRef(str(XSD) + "dateTime")
XSD.time = URIRef(str(XSD) + "time")

SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

__all__ = [
    "Graph",
    "Literal",
    "Namespace",
    "NamespaceManager",
    "RDF",
    "SKOS",
    "URIRef",
    "XSD",
    "Collection",
]

