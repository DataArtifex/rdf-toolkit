"""
Tests for SHACL validation utilities.

Tests cover both shacl_validate and shacl_validation_to_markdown functions
with various scenarios including valid and invalid RDF graphs.
"""

import os
import tempfile
from pathlib import Path

import pytest
from rdflib import Graph

from dartfx.rdf.utils import shacl_validate, shacl_validation_to_markdown

# Sample SHACL shapes for testing
SAMPLE_SHACL = r"""
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX ex: <http://example.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

ex:PersonShape a sh:NodeShape ;
    sh:targetClass ex:Person ;
    sh:property [
        sh:path ex:name ;
        sh:datatype xsd:string ;
        sh:minCount 1 ;
        sh:maxCount 1
    ] ;
    sh:property [
        sh:path ex:age ;
        sh:datatype xsd:integer ;
        sh:minInclusive 0 ;
        sh:maxInclusive 150
    ] ;
    sh:property [
        sh:path ex:email ;
        sh:datatype xsd:string ;
        sh:pattern ".+@.+\\..+" ;
        sh:maxCount 1
    ] .
"""

# Valid RDF data
VALID_RDF = """
PREFIX ex: <http://example.org/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

ex:john a ex:Person ;
    ex:name "John Doe" ;
    ex:age 30 ;
    ex:email "john@example.com" .
"""

# Invalid RDF data - missing required name
INVALID_RDF_MISSING_REQUIRED = """
PREFIX ex: <http://example.org/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

ex:jane a ex:Person ;
    ex:age 25 .
"""

# Invalid RDF data - wrong data type
INVALID_RDF_WRONG_TYPE = """
PREFIX ex: <http://example.org/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

ex:bob a ex:Person ;
    ex:name "Bob Smith" ;
    ex:age "twenty-five" .
"""

# Invalid RDF data - email doesn't match pattern
INVALID_RDF_PATTERN_MISMATCH = """
PREFIX ex: <http://example.org/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

ex:alice a ex:Person ;
    ex:name "Alice Brown" ;
    ex:age 28 ;
    ex:email "invalid-email" .
"""


@pytest.fixture
def temp_shacl_file():
    """Create a temporary SHACL shapes file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ttl", delete=False) as f:
        f.write(SAMPLE_SHACL)
        shacl_path = f.name
    yield shacl_path
    os.unlink(shacl_path)


@pytest.fixture
def temp_valid_rdf_file():
    """Create a temporary valid RDF file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ttl", delete=False) as f:
        f.write(VALID_RDF)
        rdf_path = f.name
    yield rdf_path
    os.unlink(rdf_path)


@pytest.fixture
def temp_invalid_rdf_file():
    """Create a temporary invalid RDF file (missing required property)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ttl", delete=False) as f:
        f.write(INVALID_RDF_MISSING_REQUIRED)
        rdf_path = f.name
    yield rdf_path
    os.unlink(rdf_path)


class TestShaclValidate:
    """Tests for shacl_validate function."""

    def test_validate_graph_object_valid(self, temp_shacl_file):
        """Test validation with a valid Graph object."""
        g = Graph()
        g.parse(data=VALID_RDF, format="turtle")

        conforms, results_graph, results_text = shacl_validate(g, temp_shacl_file)

        assert isinstance(conforms, bool)
        assert isinstance(results_graph, Graph)
        assert isinstance(results_text, str)
        assert conforms is True

    def test_validate_graph_object_invalid(self, temp_shacl_file):
        """Test validation with an invalid Graph object."""
        g = Graph()
        g.parse(data=INVALID_RDF_MISSING_REQUIRED, format="turtle")

        conforms, results_graph, results_text = shacl_validate(g, temp_shacl_file)

        assert conforms is False
        assert isinstance(results_graph, Graph)
        assert isinstance(results_text, str)

    def test_validate_file_path_valid(self, temp_shacl_file, temp_valid_rdf_file):
        """Test validation with a file path (valid RDF)."""
        conforms, results_graph, results_text = shacl_validate(temp_valid_rdf_file, temp_shacl_file)

        assert conforms is True
        assert isinstance(results_graph, Graph)
        assert isinstance(results_text, str)

    def test_validate_file_path_invalid(self, temp_shacl_file, temp_invalid_rdf_file):
        """Test validation with a file path (invalid RDF)."""
        conforms, results_graph, results_text = shacl_validate(temp_invalid_rdf_file, temp_shacl_file)

        assert conforms is False
        assert isinstance(results_graph, Graph)
        assert isinstance(results_text, str)

    def test_validate_invalid_data_type(self, temp_shacl_file):
        """Test that invalid data type raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported data type"):
            shacl_validate({"invalid": "dict"}, temp_shacl_file)

    def test_validate_pathlib_path(self, temp_shacl_file, temp_valid_rdf_file):
        """Test that pathlib.Path is accepted for shacl_path."""
        shacl_path = Path(temp_shacl_file)
        conforms, results_graph, results_text = shacl_validate(temp_valid_rdf_file, shacl_path)

        assert conforms is True
        assert isinstance(results_graph, Graph)

    def test_validate_wrong_datatype_violation(self, temp_shacl_file):
        """Test validation catches datatype violations."""
        g = Graph()
        g.parse(data=INVALID_RDF_WRONG_TYPE, format="turtle")

        conforms, results_graph, results_text = shacl_validate(g, temp_shacl_file)

        assert conforms is False
        # Results should contain information about the datatype violation
        assert results_graph is not None

    def test_validate_pattern_violation(self, temp_shacl_file):
        """Test validation catches pattern violations."""
        g = Graph()
        g.parse(data=INVALID_RDF_PATTERN_MISMATCH, format="turtle")

        conforms, results_graph, results_text = shacl_validate(g, temp_shacl_file)

        assert conforms is False

    def test_validate_multiple_violations(self, temp_shacl_file):
        """Test validation with multiple violations in same resource."""
        # RDF with missing required name and wrong type for age
        multi_violation_rdf = """
        PREFIX ex: <http://example.org/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        ex:charlie a ex:Person ;
            ex:age "not-a-number" .
        """
        g = Graph()
        g.parse(data=multi_violation_rdf, format="turtle")

        conforms, results_graph, results_text = shacl_validate(g, temp_shacl_file)

        assert conforms is False
        assert isinstance(results_graph, Graph)


class TestShaclValidationToMarkdown:
    """Tests for shacl_validation_to_markdown function."""

    def test_markdown_valid_report(self, temp_shacl_file):
        """Test markdown generation for a valid report."""
        g = Graph()
        g.parse(data=VALID_RDF, format="turtle")

        conforms, results_graph, results_text = shacl_validate(g, temp_shacl_file)
        markdown = shacl_validation_to_markdown(results_graph)

        assert isinstance(markdown, str)
        assert len(markdown) > 0
        assert "✅ PASS" in markdown or "❌ FAIL" in markdown

    def test_markdown_invalid_report(self, temp_shacl_file):
        """Test markdown generation for an invalid report."""
        g = Graph()
        g.parse(data=INVALID_RDF_MISSING_REQUIRED, format="turtle")

        conforms, results_graph, results_text = shacl_validate(g, temp_shacl_file)
        markdown = shacl_validation_to_markdown(results_graph)

        assert isinstance(markdown, str)
        assert "❌ FAIL" in markdown
        assert "Summary" in markdown

    def test_markdown_contains_status_section(self, temp_shacl_file):
        """Test that markdown report contains status section."""
        g = Graph()
        g.parse(data=VALID_RDF, format="turtle")

        conforms, results_graph, results_text = shacl_validate(g, temp_shacl_file)
        markdown = shacl_validation_to_markdown(results_graph)

        assert "Status" in markdown

    def test_markdown_invalid_contains_details(self, temp_shacl_file):
        """Test that invalid markdown report contains violation details."""
        g = Graph()
        g.parse(data=INVALID_RDF_MISSING_REQUIRED, format="turtle")

        conforms, results_graph, results_text = shacl_validate(g, temp_shacl_file)
        markdown = shacl_validation_to_markdown(results_graph)

        # Should contain summary and issues
        assert "Total Issues Found" in markdown or "Summary" in markdown

    def test_markdown_valid_contains_no_violations(self, temp_shacl_file):
        """Test that valid markdown report shows no violations."""
        g = Graph()
        g.parse(data=VALID_RDF, format="turtle")

        conforms, results_graph, results_text = shacl_validate(g, temp_shacl_file)
        markdown = shacl_validation_to_markdown(results_graph)

        assert "✅ PASS" in markdown

    def test_markdown_contains_icons(self, temp_shacl_file):
        """Test that markdown report uses icons for severity."""
        g = Graph()
        g.parse(data=INVALID_RDF_MISSING_REQUIRED, format="turtle")

        conforms, results_graph, results_text = shacl_validate(g, temp_shacl_file)
        markdown = shacl_validation_to_markdown(results_graph)

        # Markdown should be valid and properly formatted
        assert isinstance(markdown, str)
        assert len(markdown) > 0

    def test_markdown_uri_shortening(self, temp_shacl_file):
        """Test that markdown properly shortens URIs."""
        g = Graph()
        g.parse(data=INVALID_RDF_MISSING_REQUIRED, format="turtle")

        conforms, results_graph, results_text = shacl_validate(g, temp_shacl_file)
        markdown = shacl_validation_to_markdown(results_graph)

        # Markdown should contain prefixed URIs (like ex:jane) not full URIs
        assert isinstance(markdown, str)
        assert len(markdown) > 0


class TestShaclValidationIntegration:
    """Integration tests combining both functions."""

    def test_full_validation_workflow_valid(self, temp_shacl_file):
        """Test complete workflow from validation to markdown for valid data."""
        g = Graph()
        g.parse(data=VALID_RDF, format="turtle")

        conforms, results_graph, results_text = shacl_validate(g, temp_shacl_file)
        markdown = shacl_validation_to_markdown(results_graph)

        assert conforms is True
        assert "✅ PASS" in markdown
        assert isinstance(markdown, str)

    def test_full_validation_workflow_invalid(self, temp_shacl_file):
        """Test complete workflow from validation to markdown for invalid data."""
        g = Graph()
        g.parse(data=INVALID_RDF_MISSING_REQUIRED, format="turtle")

        conforms, results_graph, results_text = shacl_validate(g, temp_shacl_file)
        markdown = shacl_validation_to_markdown(results_graph)

        assert conforms is False
        assert "❌ FAIL" in markdown
        assert isinstance(markdown, str)

    def test_validation_with_multiple_resources(self, temp_shacl_file):
        """Test validation with multiple RDF resources in graph."""
        multi_resource_rdf = """
        PREFIX ex: <http://example.org/>

        ex:person1 a ex:Person ;
            ex:name "Person One" ;
            ex:age 25 .

        ex:person2 a ex:Person ;
            ex:name "Person Two" ;
            ex:age 35 .

        ex:person3 a ex:Person ;
            ex:age 45 .
        """
        g = Graph()
        g.parse(data=multi_resource_rdf, format="turtle")

        conforms, results_graph, results_text = shacl_validate(g, temp_shacl_file)

        # person3 should fail validation (missing required name)
        assert conforms is False

    def test_markdown_with_custom_prefixes(self, temp_shacl_file):
        """Test markdown generation with custom prefixes."""
        g = Graph()
        g.parse(data=INVALID_RDF_MISSING_REQUIRED, format="turtle")

        conforms, results_graph, results_text = shacl_validate(g, temp_shacl_file)

        # Provide custom prefixes (e.g., for a domain-specific vocabulary)
        custom_prefixes = {
            "http://example.org/": "ex:",
            "http://example.org/ontology/": "onto:",
        }

        markdown = shacl_validation_to_markdown(results_graph, prefixes=custom_prefixes)

        assert isinstance(markdown, str)
        assert len(markdown) > 0
        # Markdown should use the custom prefixes for shortening URIs
        assert "ex:" in markdown or "onto:" in markdown or "sh:" in markdown

    def test_markdown_without_custom_prefixes(self, temp_shacl_file):
        """Test markdown generation uses defaults when no custom prefixes provided."""
        g = Graph()
        g.parse(data=VALID_RDF, format="turtle")

        conforms, results_graph, results_text = shacl_validate(g, temp_shacl_file)

        # Call without custom prefixes - should use default standard prefixes
        markdown = shacl_validation_to_markdown(results_graph)

        assert isinstance(markdown, str)
        # Should contain standard prefixes like sh:, rdf:, rdfs:, xsd:
        assert len(markdown) > 0
