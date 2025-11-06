# RDF Toolkit

[![PyPI - Version](https://img.shields.io/pypi/v/hatch-foo.svg)](https://pypi.org/project/hatch-foo)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-foo.svg)](https://pypi.org/project/hatch-foo)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md)

**This project is in its early development stages. Stability is not guaranteed, and documentation is limited. We welcome your feedback and contributions.**

## Overview

This core project facilitates the implementation of Python classes for various metadata standards and serialization to RDF formats.

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
   pip install -e .
   ```

## Usage

### Serialising Pydantic models to RDF

The toolkit ships with a lightweight integration that lets you decorate
Pydantic models with RDF metadata and convert them directly to and from
`rdflib` graphs. The integration is provided by the
``dartfx.rdf.pydantic_rdf`` module.

```python
from typing import Annotated

from rdflib import Namespace

from dartfx.rdf.pydantic_rdf import RdfBaseModel, RdfProperty

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

See the [Pydantic RDF integration guide](docs/source/pydantic_rdf.rst) for a
deeper walk-through including language-tagged strings, custom datatypes and
subject selection.

## Roadmap
- Migrate model from Python @dataclass to Pydantic
- Explore transitioning into RDF annotation and serializer from [DCAT SeMPyRO project](https://github.com/Health-RI/SeMPyRO)
- Peer testing and validation
- RDF deserializer (from graph to Python)

## Contributing
 
1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D
