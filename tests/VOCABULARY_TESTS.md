# RDF Toolkit Vocabulary Test Coverage

## Summary
Successfully created and refined comprehensive test coverage for the RDF Toolkit vocabulary models. All tests are now **passing (60/60 ✅)**.

## Test Results Overview

### Current Status
- **Total Tests**: 60
- **Passing**: 60 ✅ (100%)
- **Core RDF Tests**: 8/8 passing
- **Vocabulary Tests**: 43/43 passing
- **Benchmark Tests**: 4/4 passing
- **Edge-Case Tests**: 3/3 passing
- **Integration Tests**: 2/2 passing

### Test Results
```
============================== 60 passed in 3.69s ==============================
```

## Test Collections

### Core RDF Tests (8 tests - all passing)
- `test_pydantic_rdf.py` - Core Pydantic RDF serialization
- `test_nested_serialization.py` - Nested object handling

### Vocabulary Tests (43 tests - all passing)

| Vocabulary | Tests | Status | Coverage |
|-----------|-------|--------|----------|
| FOAF (Friend of a Friend) | 5 | ✅ | Document, Person, Organization, Agent |
| SKOS (Knowledge Org) | 6 | ✅ | Concept, ConceptScheme, Collection, Labels |
| PROV (Provenance) | 7 | ✅ | Entity, Activity, Agent, Derivation |
| SPDX | 4 | ✅ | Package, SpdxDocument |
| VCard | 6 | ✅ | Individual, Organization, Contact Info |
| DCTERMS (Dublin Core Terms) | 5 | ✅ | Record, Agent, Dates, Contributors |
| ODRL | 5 | ✅ | Policy, Permission, Prohibition, Constraint |
| XKOS | 5 | ✅ | ClassificationLevel, Concepts, Correspondence |

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

#### 6. DCTERMS (Dublin Core Terms) - 5 tests ✅
- DublinCoreRecord serialization and round-trip
- Date and periodicity fields
- Contributor lists
- Agent model serialization

#### 7. ODRL - 5 tests ✅
- Policy serialization and round-trip
- Permission and Action relationships
- Prohibition with remedy
- Constraint fields

#### 8. XKOS - 5 tests ✅
- ClassificationLevel serialization
- StatisticalConcept and StatisticalClassification
- Correspondence with associations
- Full round-trip serialization

### Benchmark Tests (4 tests - all passing)
- FOAF graph serialization
- FOAF graph deserialization
- DCTERMS round-trip serialization
- ODRL policy round-trip serialization

### Edge-Case Tests (3 tests - all passing)
- Null values and empty lists are skipped
- Empty list round-trip defaults
- Circular references via URIRefs

### Integration Tests (2 tests - all passing)
- Multi-vocabulary graph round-trip
- SKOS/XKOS shared graph serialization

## Test Files Structure
```
tests/
├── test_pydantic_rdf.py           # Core RDF tests (8)
├── test_nested_serialization.py   # Nested object tests
├── test_edge_cases.py             # Edge-case tests (3)
├── test_benchmarks_serialization.py # Benchmark tests (4)
├── test_integration_multivocab.py # Integration tests (2)
├── test_vocabularies_foaf.py      # FOAF vocab tests (5)
├── test_vocabularies_skos.py      # SKOS vocab tests (6)
├── test_vocabularies_prov.py      # PROV vocab tests (7)
├── test_vocabularies_spdx.py      # SPDX vocab tests (4)
├── test_vocabularies_vcard.py     # VCard vocab tests (6)
├── test_vocabularies_dcterms.py   # DCTERMS vocab tests (5)
├── test_vocabularies_odrl.py      # ODRL vocab tests (5)
└── test_vocabularies_xkos.py      # XKOS vocab tests (5)
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
- `Agent(id="...")` - DCTERMS Agent requires ID

### Models with Optional Fields
- All FOAF models can be created empty
- PROV models (Entity, Activity, Agent) can be created empty
- SPDX models can be created empty
- VCard models require `fn` (formatted name) field

## Coverage Highlights

### ✅ Accomplished
- All 8 original RDF tests passing
- All 43 vocabulary tests passing
- All 4 benchmark tests passing
- All 3 edge-case tests passing
- All 2 integration tests passing
- 100% success rate
- Round-trip serialization verified for each vocabulary
- RDF graph generation verified
- Proper subject URI extraction from graphs

## Next Steps (Optional)

To expand coverage further:
1. Add SPARQL validation for multi-vocabulary graphs

## Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run only vocabulary tests
uv run pytest tests/test_vocabularies_*.py -v

# Run benchmarks only
uv run pytest tests/test_benchmarks_serialization.py --benchmark-only

# Save a benchmark baseline
uv run pytest tests/test_benchmarks_serialization.py --benchmark-only --benchmark-save=baseline

# Compare against a saved baseline
uv run pytest tests/test_benchmarks_serialization.py --benchmark-only --benchmark-compare=baseline

# Run with coverage
uv run pytest tests/ --cov=dartfx.rdf --cov-report=term-missing
```

## Notes
- All tests follow the same pattern for consistency
- Tests verify both graph generation and round-trip serialization
- Subject URIs are extracted from the RDF graph, not regenerated
- All vocabulary models inherit from appropriate base classes with proper RDF type configuration
- Field names align with vocabulary specifications
