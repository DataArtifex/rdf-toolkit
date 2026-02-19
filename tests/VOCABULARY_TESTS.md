# RDF Toolkit Vocabulary Test Coverage

## Summary
Successfully created and refined comprehensive test coverage for the RDF Toolkit vocabulary models. All tests are now **passing (36/36 ✅)**.

## Test Results Overview

### Current Status
- **Total Tests**: 36
- **Passing**: 36 ✅ (100%)
- **Core RDF Tests**: 8/8 passing
- **Vocabulary Tests**: 28/28 passing

### Test Results
```
============================== 36 passed in 0.55s ==============================
```

## Test Collections

### Core RDF Tests (8 tests - all passing)
- `test_pydantic_rdf.py` - Core Pydantic RDF serialization
- `test_nested_serialization.py` - Nested object handling

### Vocabulary Tests (28 tests - all passing)

| Vocabulary | Tests | Status | Coverage |
|-----------|-------|--------|----------|
| FOAF (Friend of a Friend) | 5 | ✅ | Document, Person, Organization, Agent |
| SKOS (Knowledge Org) | 6 | ✅ | Concept, ConceptScheme, Collection, Labels |
| PROV (Provenance) | 7 | ✅ | Entity, Activity, Agent, Derivation |
| SPDX | 4 | ✅ | Package, SpdxDocument |
| VCard | 6 | ✅ | Individual, Organization, Contact Info |

#### 1. FOAF (Friend of a Friend) - 5 tests ✅
- Document serialization and round-trip
- Person, Organization, Agent models
- Full round-trip serialization

#### 2. SKOS (Simple Knowledge Organization System) - 6 tests ✅
- Concept and ConceptScheme models
- Alternative labels and definitions
- Scope notes
- Collection handling with ID requirement
- Full round-trip serialization

#### 3. PROV (Provenance Ontology) - 7 tests ✅
- Entity, Activity, Agent models
- Derivation relationships
- Attribution handling
- Entity usage tracking
- Full round-trip serialization

#### 4. SPDX - 4 tests ✅
- Package and SpdxDocument models
- Basic serialization with metadata
- Round-trip serialization

#### 5. VCard - 6 tests ✅
- Individual and Organization models
- Nicknames and URLs
- Notes and contact information
- Full round-trip serialization

## Test Files Structure
```
tests/
├── test_pydantic_rdf.py           # Core RDF tests (8)
├── test_nested_serialization.py   # Nested object tests
├── test_vocabularies_foaf.py      # FOAF vocab tests (5)
├── test_vocabularies_skos.py      # SKOS vocab tests (6)
├── test_vocabularies_prov.py      # PROV vocab tests (7)
├── test_vocabularies_spdx.py      # SPDX vocab tests (4)
└── test_vocabularies_vcard.py     # VCard vocab tests (6)
```

## Key Implementation Details

### Issue Resolved
The primary challenge was understanding that `_subject_uri()` generates a new UUID each time it's called. The solution was to extract the actual subject URI from the RDF graph using `RDF.type` queries.

### Pattern Used
For all tests:
```python
# Extract subject from RDF graph (not regenerating with _subject_uri())
subjects = list(graph.subjects(RDF.type, MODEL_TYPE))
assert len(subjects) > 0
reloaded = Model.from_rdf_graph(graph, subjects[0])
```

### RDF Type Mappings
- FOAF models use `FOAF.*` types (Person, Organization, Document, Agent)
- SKOS models use `SKOS.*` types (Concept, ConceptScheme, Collection)
- PROV models use `PROV.*` types (Entity, Activity, Agent)
- SPDX models use `SPDX.*` types (Package, SpdxDocument)
- VCard models use `VCARD.*` types (Individual, Organization)

## Model Requirements

### Models with Required Fields
- `Collection(id="...")` - SKOS Collection requires ID
- `Concept(id="...", pref_label=[...])` - SKOS Concept requires ID
- `ConceptScheme(id="...", pref_label=[...])` - SKOS ConceptScheme requires ID
- `DublinCoreRecord(id="...")` - DCTERMS requires ID

### Models with Optional Fields
- All FOAF models can be created empty
- PROV models (Entity, Activity, Agent) can be created empty
- SPDX models can be created empty
- VCard models require `fn` (formatted name) field

## Coverage Highlights

### ✅ Accomplished
- All 8 original RDF tests passing
- All 28 vocabulary tests passing
- 100% success rate
- Round-trip serialization verified for each vocabulary
- RDF graph generation verified
- Proper subject URI extraction from graphs

## Next Steps (Optional)

To expand coverage further:
1. Create comprehensive tests for DCTERMS vocabulary (requires ID field)
2. Create comprehensive tests for ODRL vocabulary (complex relationships)
3. Create comprehensive tests for XKOS vocabulary (complex relationships)
4. Add edge-case tests (null values, empty lists, circular references)
5. Add performance benchmarks for serialization/deserialization

## Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run only vocabulary tests
uv run pytest tests/test_vocabularies_*.py -v

# Run with coverage
uv run pytest tests/ --cov=dartfx.rdf --cov-report=term-missing
```

## Notes
- All tests follow the same pattern for consistency
- Tests verify both graph generation and round-trip serialization
- Subject URIs are extracted from the RDF graph, not regenerated
- All vocabulary models inherit from appropriate base classes with proper RDF type configuration
- Field names align with vocabulary specifications
