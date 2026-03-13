# Advanced RDF URI Generation in `rdf-toolkit`

In the world of Linked Data, every resource MUST have a globally unique and stable identifier. In RDF, this is typically a URI (Uniform Resource Identifier). Managing these identifiers manually in code can be error-prone and lead to brittle systems. The `rdf-toolkit` solves this by providing a declarative, powerful system for **RDF URI Generation**.

## 1. Implementation Overview

At the heart of `rdf-toolkit`'s URI generation is the `RdfUriGenerator` protocol. This protocol defines a simple interface for any callable that can take a model instance and produce an `rdflib.URIRef` or `rdflib.BNode`.

Any `RdfBaseModel` can specify its generation strategy through the `rdf_uri_generator` class attribute:

```python
class MyModel(RdfBaseModel):
    rdf_uri_generator = MyCustomGenerator()
    ...
```

When you call `to_rdf()` or `to_rdf_graph()`, the toolkit automatically invokes the assigned generator to determine the subject URI for that specific resource.

## 2. Benefits of the Approach

*   **Declarative Logic**: Move URI construction logic out of your business code and into the model definition.
*   **Stability**: Ensure that resources get the same URI every time they are serialized, which is critical for deduplication and joining graphs.
*   **Flexibility**: Easily switch between UUIDs, template-based URIs, or content-addressable (hash) URIs without changing your data structure.
*   **Fail-safe Defaults**: If a required field is missing for a structured URI, generators can gracefully fall back to Blank Nodes (BNodes) to prevent malformed data.
*   **Composition**: Stack multiple strategies (e.g., "try field X, then field Y, then fall back to a hash").

## 3. Available Generators

The `rdf-toolkit` provides several built-in generators in `dartfx.rdf.pydantic._uri_generators`:

| Generator | Description |
| :--- | :--- |
| **`DefaultUriGenerator`** | The standard "pragmatic" strategy: uses an explicit ID field if present, otherwise mints a UUID (or BNode if `auto_uuid=False`). |
| **`TemplateUriGenerator`** | Uses Python's `format_map` to build a URI from multiple model fields (e.g., `https://api.example.com/items/{category}/{slug}`). |
| **`HashUriGenerator`** | Creates "content-addressable" URIs by hashing specific fields. Guarantees the same URI for the same data content. |
| **`PrefixedUriGenerator`** | A lightweight helper that simply appends a field value to a fixed prefix. |
| **`CompositeUriGenerator`** | Wraps multiple generators and returns the result of the first one that successfully produces a `URIRef`. |

## 4. Which One to Choose?

Choosing the right strategy depends on your data's nature and where it comes from:

*   **Natural Primary Key exists**: Use `DefaultUriGenerator` or `PrefixedUriGenerator`.
*   **Deep Hierarchical Identity**: Use `TemplateUriGenerator` to bake the hierarchy into the URI path.
*   **No Stable ID available (Deduplication needed)**: Use `HashUriGenerator` to ensure identical objects across different systems get the same URI based on their content.
*   **Anonymous / Intermediate Data**: Use `DefaultUriGenerator(auto_uuid=False)` to produce clean RDF Blank Nodes.
*   **Complex Fallback Logic**: Use `CompositeUriGenerator` to prioritize multiple identification strategies.

## 5. Comprehensive Example

The following examples demonstrate how to set up each built-in generator and the resulting subject URIs they produce.

```python
from typing import Annotated, Optional, List
from rdflib import Namespace, DCTERMS, SCHEMA
from dartfx.rdf.pydantic import RdfBaseModel, RdfProperty, DefaultUriGenerator
from dartfx.rdf.pydantic._uri_generators import (
    TemplateUriGenerator,
    HashUriGenerator,
    CompositeUriGenerator,
    PrefixedUriGenerator
)

EX = Namespace("https://example.org/")

# --- 1. DefaultUriGenerator (Standard) ---
# Goal: Use 'id' if present, otherwise mint a UUID.
class User(RdfBaseModel):
    rdf_namespace = EX
    id: Optional[str] = None
    name: str

# Result with ID: <https://example.org/bob>
u1 = User(id="bob", name="Bob", rdf_uri_generator=DefaultUriGenerator(auto_uuid=True))

# Result with UUID: <https://example.org/5f3a...>
u2 = User(name="Alice", rdf_uri_generator=DefaultUriGenerator(auto_uuid=True))


# --- 2. DefaultUriGenerator (Blank Node fallback) ---
# Goal: Use 'id' if present, otherwise keep it anonymous (Blank Node).
class Note(RdfBaseModel):
    rdf_namespace = EX
    id: Optional[str] = None
    content: str

# Result: _:n123... (rdflib.BNode)
n = Note(content="Important reminder", rdf_uri_generator=DefaultUriGenerator(auto_uuid=False))


# --- 3. TemplateUriGenerator ---
# Goal: Build a structured path from multiple model fields.
class Dataset(RdfBaseModel):
    rdf_namespace = EX
    year: int
    slug: str

# Result: <https://example.org/datasets/2024/weather>
ds = Dataset(
    year=2024,
    slug="weather",
    rdf_uri_generator=TemplateUriGenerator("https://example.org/datasets/{year}/{slug}")
)


# --- 4. HashUriGenerator ---
# Goal: Deterministic URI based on content (Deduplication).
class Observation(RdfBaseModel):
    rdf_namespace = EX
    timestamp: str
    sensor_id: str

# Result: <https://example.org/obs/a9e2f...> (SHA256 of fields)
obs = Observation(
    timestamp="2024-03-13",
    sensor_id="SN-001",
    rdf_uri_generator=HashUriGenerator(namespace="https://example.org/obs/", fields=["timestamp", "sensor_id"])
)


# --- 5. PrefixedUriGenerator ---
# Goal: Simple concatenation of a prefix and a single field.
class Concept(RdfBaseModel):
    code: str

# Result: <https://example.org/C001>
c = Concept(code="C001", rdf_uri_generator=PrefixedUriGenerator(prefix=EX, field="code"))


# --- 6. CompositeUriGenerator ---
# Goal: Try strategies in order (Priority Chain).
class Publication(RdfBaseModel):
    rdf_namespace = EX
    id: Optional[str] = None
    title: str

# Result (Id is None, falls back to hash): <https://example.org/pub/d4f21...>
p = Publication(
    title="Annual Report",
    rdf_uri_generator=CompositeUriGenerator(
        DefaultUriGenerator(auto_uuid=False),
        HashUriGenerator("https://example.org/pub/", ["title"])
    )
)
```

## 6. Conclusions

Robust URI generation is the foundation of high-quality Linked Data. By treating URI generation as a first-class, declarative component of your models, `rdf-toolkit` ensures that your data remains discoverable, joinable, and logically sound. Whether you need the global uniqueness of UUIDs, the structural clarity of templates, or the deterministic nature of hashes, the toolkit provides the right tool for every use case.
