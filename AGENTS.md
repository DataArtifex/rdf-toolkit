# AI Agent Instructions

Welcome, fellow AI. This file provides context and instructions for working on this repository effectively.

## Project Objectives

This toolkit provides **type-safe RDF serialization for Python** by bridging Pydantic models with RDF graphs. The core goals are:

### Primary Objectives

1. **Seamless Pydantic-RDF Integration**: Enable Python developers to work with RDF data using familiar Pydantic models with full validation, type safety, and IDE support.

2. **Standards Compliance**: Provide pre-built, validated Pydantic models for common RDF vocabularies (FOAF, PROV, DCTERMS, SKOS, SPDX, ODRL, VCard, XKOS) that correctly implement their specifications.

3. **Bidirectional Conversion**: Support lossless round-trip conversion between Python objects and RDF graphs in multiple serialization formats (Turtle, RDF/XML, JSON-LD, N-Triples, etc.).

4. **Developer Experience**: Minimize boilerplate while maximizing flexibility through declarative field annotations, automatic namespace management, and sensible defaults.

### AI Agent Guidelines for This Project

**When adding new features:**
- Maintain backward compatibility with existing RdfBaseModel implementations
- Ensure all new RDF property mappings are tested with round-trip serialization/deserialization
- Document any new RdfProperty parameters with examples in docstrings
- Consider how changes affect both simple literals and complex nested object graphs

**When fixing bugs:**
- Test with both `Union[T, None]` and `T | None` type annotation syntaxes (Python 3.10+ compatibility)
- Verify fixes work with list fields, nested RdfBaseModel instances, and primitive types
- Check that rdflib namespace handling remains compatible (especially with DefinedNamespace metaclasses)
- Run the full test suite including nested serialization tests

**When adding vocabulary models:**
- Inherit from `RdfBaseModel` and define `rdf_type`, `rdf_namespace`, and `rdf_prefixes` as `ClassVar`
- Use `Annotated[Type, RdfProperty(predicate)]` for all RDF-mapped fields
- Include docstrings referencing the official vocabulary specification
- Add comprehensive examples showing typical usage patterns
- Test serialization produces valid RDF that conforms to the vocabulary standard

**Type Checking Considerations:**
- All `rdf_type`, `rdf_namespace`, and `rdf_prefixes` class attributes MUST use `ClassVar` annotations
- Use `# type: ignore[...]` comments sparingly and document why (e.g., rdflib namespace metaclass limitations)
- Pyrefly configuration is defined under `[tool.pyrefly]` in pyproject.toml
- The package requires a `py.typed` marker file for PEP 561 compliance

## Project Stack

- **Language**: Python 3.12+ (Strictly required)
- **Dependency Management & Workflow**: [uv](https://github.com/astral-sh/uv) (Recommended) and [Hatch](https://hatch.pypa.io/).
- **Linting & Formatting**: [Ruff](https://beta.astral.sh/ruff/) (extremely fast linter/formatter).
- **Git Hooks**: [pre-commit](https://pre-commit.com/) (ensures code quality before commits).
- **Testing**: [pytest](https://docs.pytest.org/) with [coverage](https://coverage.readthedocs.io/).
- **Documentation**: [Sphinx](https://www.sphinx-doc.org/) with [MyST-Parser](https://myst-parser.readthedocs.io/) (Markdown support) and [Read the Docs theme](https://sphinx-rtd-theme.readthedocs.io/).
- **Version Control**: Git.

## Bootstrapping a New Project

To rename the project and package from the template defaults:
1. Run `./rename.sh "new-project-name" "new_package_name"`
2. Run `uv sync` to refresh the environment.
3. **DeepWiki**: Register the new project at [DeepWiki.com](https://deepwiki.com/) to enable AI-optimized documentation indexing.

## Environment Management

This project uses `hatch` for environment management, but `uv` is preferred for speed.

- To run tests: `uv run pytest` or `hatch run test`
- To check types: `hatch run types:check`
- To build docs: `hatch run docs:build`

## Coding Standards

- Follow PEP 8.
- Use type hints for all public APIs.
- Docstrings should be in Google style or NumPy style (Sphinx compatible).
- Prefer `pathlib` over `os.path`.
- Prefer Pydantic for modeling over Python dataclasses or other similar packages.
- Prefer Polars package for data management over Pandas or other similar package.
- Strictly follow the project's Ruff configuration. Run `uv run ruff check .` and `uv run ruff format .` to ensure compliance before submitting changes.

## Testing Policy

- All new features must be accompanied by tests.
- Maintain or improve test coverage.
- Use `pytest` fixtures for setup/teardown.
- Tests are located in the `tests/` directory.

## Documentation Policy

- Documentation is located in the `docs/source` directory.
- Main documentation is in `.rst` or `.md` (via MyST).
- Keep `README.md` up to date with core installation and usage instructions.
- Keep a dedicated `IMPLEMENTATION.md` document up to date that describes the package/code technical implementation.
- Maintain `CHANGELOG.md` with every significant change, ensuring the latest version is always at the top using the version number as heading (e.g., `## [0.1.0]`). Use short, concise bullet points.

## Version Management

- This project uses **dynamic versioning** via Hatch.
- The source of truth for the version is located in: `src/dartfx/rdf/__about__.py`.
- To bump versions, modify that file manually or use `hatch version <segment>` (e.g., `hatch version minor`).
- Follow [Semantic Versioning (SemVer)](https://semver.org/).

## Secret Management

- **Local Development**: Use a `.env` file in the project root for local environment variables and secrets.
- **Loading**: Secrets are automatically loaded in tests via `tests/conftest.py` using `python-dotenv`.
- **Git Hygiene**: Never commit `.env` files. Ensure they are covered by `.gitignore`.
- **CI/CD**: Add secrets to GitHub Repository Secrets for use in GitHub Actions. Reference them in workflows as `${{ secrets.SECRET_NAME }}`.

## GitHub Actions CI/CD

- **CI**: Located in `.github/workflows/test.yml`. Runs tests and linting on push/PR to `main` across Ubuntu, macOS, and Windows.
- **Docs**: Located in `.github/workflows/sphinx.yaml`. Builds and deploys documentation to GitHub Pages on push to `main`.
- All workflows use `astral-sh/setup-uv` for fast execution and caching.

## Working with this Repo

1. **Analysis**: Always start by reviewing `pyproject.toml` and `src/` structure.
2. **Context**: Check `KIs` (Knowledge Items) if available for specific domain logic.
3. **Execution**: Use `uv` or `hatch` for running scripts and tests.
4. **Validation**: Always run `pytest` before finalizing changes.
