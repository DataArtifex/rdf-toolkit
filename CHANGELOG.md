# Changelog

All notable changes to this project will be documented in this file.

## [2026-02-26]

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
