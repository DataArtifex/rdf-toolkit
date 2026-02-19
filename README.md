# RDF Toolkit

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/DataArtifex/rdf-toolkit)
[![Documentation](https://img.shields.io/badge/docs-v6-blue)](https://www.dataartifex.org/docs/rdf-toolkit/)
[![Package Status](https://img.shields.io/badge/PyPI-not%20published-lightgrey)](https://github.com/DataArtifex/rdf-toolkit)
[![CI](https://github.com/DataArtifex/rdf-toolkit/actions/workflows/test.yml/badge.svg)](https://github.com/DataArtifex/rdf-toolkit/actions/workflows/test.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md)
[![License](https://img.shields.io/github/license/DataArtifex/rdf-toolkit.svg)](https://github.com/DataArtifex/rdf-toolkit/blob/main/LICENSE.txt)

## Overview

This toolkit provides type-safe Pydantic models for standard vocabularies and enables round-trip serialization to and from RDF formats.

## Installation

### PyPI Release

Once stable, this package will be officially released and distributed through [PyPI](https://pypi.org/). Stay tuned for updates!

### Local Installation

In the meantime, you can install the package locally by following these steps:

1. **Clone the Repository:**

   First, clone the repository to your local machine:

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install the Package:**

    From the project's home directory, run the following command to install the package:

    ```bash
    uv pip install -e .
    ```

## Usage

### Serialising Pydantic models to RDF

The toolkit ships with a lightweight integration that lets you decorate
Pydantic models with RDF metadata and convert them directly to and from
`rdflib` graphs. The integration is provided by the
`dartfx.rdf.pydantic` module.

```python
from typing import Annotated

from rdflib import Namespace, URIRef

from dartfx.rdf.pydantic import RdfBaseModel, RdfProperty

EX = Namespace("https://example.com/ns/")


class Project(RdfBaseModel):
    rdf_type = EX.Project
    rdf_namespace = EX
    rdf_prefixes = {"ex": EX}

    id: str
    name: Annotated[str, RdfProperty(EX.name)]
    homepage: Annotated[str, RdfProperty(EX.homepage)]


project = Project(id="rdftoolkit", name="RDF Toolkit", homepage="https://example.com/toolkit")

turtle = project.to_rdf(format="turtle")
print(turtle)
```

The ``RdfProperty`` metadata describes which predicate should be used for each
field. When ``rdf_namespace`` is supplied the toolkit automatically builds URIs
for identifiers that are not already absolute. The resulting RDF graph is a
standard ``rdflib.Graph`` instance, so you can serialise it to any format that
``rdflib`` supports by switching the ``format`` argument.

### Deserialising RDF into models

The same annotations are used to parse RDF back into Pydantic models. When a
model specifies ``rdf_type`` the deserialiser will look for a matching subject
and populate the fields from the graph.

```python
loaded = Project.from_rdf(turtle, format="turtle")
assert loaded == project
```

Nested models and multi-valued properties are also supported. Declare lists of
annotated fields, or embed other ``RdfBaseModel`` subclasses, and the toolkit
will recursively serialise and deserialise them.

### Working with URIs and Datatypes

The toolkit provides several ways to handle URIs and specific XSD datatypes:

- **Resource Identifiers**: Use `rdflib.URIRef` as a type hint for fields that should be serialized as RDF resources.
- **XSD Datatypes**: Specify the `datatype` in `RdfProperty` to force a literal value to a specific XSD type (e.g., `XSD.anyURI`, `XSD.integer`).
- **Validation**: Combine with Pydantic's built-in types like `AnyUrl` for strict input validation.

```python
from typing import Annotated, Optional
from pydantic import AnyUrl
from rdflib import XSD, SCHEMA, URIRef
from dartfx.rdf.pydantic import RdfBaseModel, RdfProperty

class WebResource(RdfBaseModel):
    # Serialized as an RDF resource (URIRef)
    see_also: Annotated[Optional[URIRef], RdfProperty(SCHEMA.seeAlso)] = None

    # Validated by Pydantic, serialized as "..."^^xsd:anyURI literal
    url: Annotated[AnyUrl, RdfProperty(SCHEMA.url, datatype=XSD.anyURI)]
```

See the [Pydantic RDF integration guide](docs/source/pydantic_rdf.rst) for a
deeper walk-through including language-tagged strings, custom datatypes and
subject selection.

## Supported Vocabularies

The toolkit provides Pydantic models for the following vocabularies:

- **DCTERMS**: Dublin Core Metadata Initiative Terms
- **FOAF**: Friend of a Friend
- **ODRL**: Open Digital Rights Language
- **PROV**: PROV Ontology
- **SKOS**: Simple Knowledge Organization System (including SKOS-XL)
- **SPDX**: Software Package Data Exchange
- **VCARD**: vCard / Virtual Contact File
- **XKOS**: Extended Knowledge Organization System

## Testing

```bash
# Run all tests
uv run pytest tests/ -v

# Run only vocabulary tests
uv run pytest tests/test_vocabularies_*.py -v

# Run benchmarks only
uv run pytest tests/test_benchmarks_serialization.py --benchmark-only
```

## Roadmap
- [x] Migrate model from Python @dataclass to Pydantic
- [x] Explore transitioning into RDF annotation and serializer from [DCAT SeMPyRO project](https://github.com/Health-RI/SeMPyRO)
- [x] RDF deserializer (from graph to Python)
- [ ] Peer testing and validation
- [ ] Expand vocabulary coverage
- [ ] Improve documentation

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D
