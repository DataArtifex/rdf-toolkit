# Changelog

All notable changes to this project will be documented in this file.

## [2026-02-26]

### Added
- Flexible property types (`T | list[T]`) across all vocabulary models.
- Core support in `RdfBaseModel` for automatic scalar-to-list wrapping during serialization.
- Improved string-to-URIRef coercion for `Union` types in `_base.py`.
- New test suite `tests/test_flexible_input.py` covering all major vocabularies.

### Changed
- Updated SKOS, FOAF, DCTERMS, PROV, ODRL, SPDX, VCARD, and XKOS models to support single values.
- Refactored `_field_type_info` to correctly resolve Python 3.10+ `|` union types.
- Standardized RDF property annotations to use `Annotated[T | list[T] | None, RdfProperty(...)]`.

### Fixed
- Issue where Pydantic validation failed when providing single strings to list-typed RDF properties.
- Incomplete Union type resolution in `_get_rdf_model_type` for nested models.
