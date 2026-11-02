# Multi-Type and Polymorphic RDF Support in `rdf-toolkit`

## Overview

In Semantic Web specifications and real-world multi-profile schemas (such as the Cross-Domain Interoperability Framework / CDIF combining Schema.org and DDI-CDI), RDF resources frequently possess multiple types:

```json
{
  "@id": "http://example.org/dataset#variable-1",
  "@type": ["schema:PropertyValue", "cdi:InstanceVariable"],
  "schema:name": "variable-1"
}
```

`rdf-toolkit` (`dartfx-rdf`) supports both **static multi-typing** and **dynamic unmodeled type preservation**, alongside **graph-aware polymorphic dispatch**.

---

## 1. Static Multi-Typing

A model class declares multiple types via `rdf_type: ClassVar`:

```python
from typing import Annotated, ClassVar
from rdflib import Namespace
from dartfx.rdf.pydantic import RdfBaseModel, RdfProperty

SCHEMA = Namespace("http://schema.org/")
CDI = Namespace("http://ddialliance.org/Specification/DDI-CDI/1.0/RDF/")

class CDIFInstanceVariable(RdfBaseModel):
    rdf_type: ClassVar = [SCHEMA.PropertyValue, CDI.InstanceVariable]
    rdf_prefixes: ClassVar = {"schema": SCHEMA, "cdi": CDI}

    id: str | None = None
    name: Annotated[str | None, RdfProperty(SCHEMA.name)] = None
```

- Accepts `list`, `tuple`, `set`, single `URIRef`, or single `str`.
- Serializing with `to_rdf()` emits separate `(subject, RDF.type, type_uri)` triples for all declared classes.
- Deserializing with `from_rdf()` without an explicit subject queries the intersection of all declared classes to unambiguously locate the target node.

---

## 2. Dynamic Unmodeled Type Preservation

When importing data from third-party RDF graphs, resources often have additional classes attached that are not relevant to your local Pydantic domain models.

By default (`rdf_preserve_unmodeled_types: ClassVar[bool] = True`):
- `from_rdf_graph` saves any unmodeled `(subject, RDF.type, ?t)` triples in a private instance set `_extra_rdf_types`.
- `to_rdf_graph` re-emits them on export.
- Result: **Lossless round-trip** without needing to define every auxiliary external class in Pydantic.

### Strict Canonical Exports
If you want to sanitize or normalize graphs on export, set:
```python
class StrictModel(RdfBaseModel):
    rdf_type: ClassVar = CDI.InstanceVariable
    rdf_preserve_unmodeled_types: ClassVar = False  # Drop extra graph types on export
```

---

## 3. Polymorphic Union Dispatch

When nested properties define a union of models, such as:

```python
class Dataset(RdfBaseModel):
    rdf_type: ClassVar = SCHEMA.Dataset
    elements: Annotated[
        list[CDIFInstanceVariable | PlainPropertyValue],
        RdfProperty(SCHEMA.variableMeasured),
    ] = []
```

`from_rdf_graph` does not naively pick the first model in the `Union`. Instead:
1. Queries the graph for the candidate node's `(node, RDF.type, ?)` triples.
2. Evaluates candidate models based on declared type subset matches and overlap count.
3. Automatically instantiates the most specific matching Pydantic model (`CDIFInstanceVariable` when both classes are present, or `PlainPropertyValue` when only `schema:PropertyValue` is present).
