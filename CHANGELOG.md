# Changelog

All notable changes to this project will be documented in this file.

## [0.1.2]

### Added
- New `LangString` frozen Pydantic model for representing language-tagged RDF literals.
- New `LangStringList` class (extends `list[LangString]`) with convenience methods:
  - Query: `count_by_lang`, `has_language`, `has_untagged`, `has_synonyms`, `languages`, `untagged`, `get_by_language`.
  - Mutation: `append`, `extend`, `+=`, `-=`, `-` with automatic `(value, lang)` deduplication.
  - Str-like: `__str__` and `__eq__` return the plain string value when a single entry or single untagged entry exists.
- New `LocalizedStr` type alias (backed by `LangStringList`) that coerces any flexible input (str, dict, LangString, list) into canonical `LangStringList` storage.
- Comprehensive Sphinx documentation with input tables, query/mutation examples, and RDF round-trip guide.

### Changed
- Refactored all vocabulary models (SKOS, DCTERMS, FOAF, ODRL, PROV, SPDX, VCARD, XKOS) to use `LocalizedStr` for textual properties.
- `LocalizedStr` fields now always store a `LangStringList` internally instead of a union of str/dict/list types.
- Updated serialization (`_serialise_into_graph`) with a fast path for `LangStringList` fields.
- Updated deserialization (`from_rdf_graph`) to produce `LangStringList` directly.

### Breaking Changes
- `LocalizedStr` fields now return `LangStringList` (a `list[LangString]` subclass) instead of plain `str` or `dict`. Code using `== "string"` comparisons will still work for single-entry or single-untagged-entry fields due to str-like behaviour. Code using `isinstance(field, str)` or `isinstance(field, dict)` checks must be updated.

## [0.1.1]

### Added
- Flexible property types (`T | list[T]`) across all vocabulary models.
- Core support in `RdfBaseModel` for automatic scalar-to-list wrapping during serialization.
- Smart scalar deserialization: single RDF values round-trip as scalars instead of single-element lists.
- Improved string-to-URIRef coercion for `Union` types in `_base.py`.
- New test suite `tests/test_flexible_input.py` covering all major vocabularies.

### Changed
- Updated SKOS, FOAF, DCTERMS, PROV, ODRL, SPDX, VCARD, and XKOS models to support single values.
- Refactored `_field_type_info` to return a 3-tuple `(is_list, accepts_scalar, inner_type)` for flexible type introspection.
- Standardized RDF property annotations to use `Annotated[T | list[T] | None, RdfProperty(...)]`.
- Deserializer now returns a scalar when a field accepts both `T` and `list[T]` and only one value exists in the graph.

### Breaking Changes
- `from_rdf_graph` / `from_rdf` now return scalars instead of single-element lists for fields typed `T | list[T] | None` when only one RDF value exists. Downstream code using index access (e.g., `obj.title[0]`) or `len()` on such fields must handle both `str` and `list[str]`.

### Fixed
- Issue where Pydantic validation failed when providing single strings to list-typed RDF properties.
- Incomplete Union type resolution in `_get_rdf_model_type` for nested models.
- Restored missing `Association`, `End`, and `Start` class definitions in PROV vocabulary module.
