"""Test XKOS expansion."""

from dartfx.rdf.pydantic.xkos import (
    ClassificationLevel, StatisticalConcept, StatisticalClassification, XKOS
)
from rdflib import URIRef

def test_classification_level_properties():
    """Test new properties on ClassificationLevel."""
    level = ClassificationLevel(
        id="level1",
        organized_by=["http://example.com/concept/division"],
        notation_pattern=["[A-Z]{2}"],
        max_length=[2]
    )
    
    turtle = level.to_rdf(format="turtle")
    print("ClassificationLevel Turtle:")
    print(turtle)
    
    assert "xkos:organizedBy" in turtle
    assert "xkos:notationPattern" in turtle
    assert "xkos:maxLength" in turtle

def test_statistical_concept_properties():
    """Test new properties on StatisticalConcept."""
    concept = StatisticalConcept(
        id="concept1",
        disjoint=["http://example.com/concept/concept2"],
        broader_generic=["http://example.com/concept/broader"],
        introduction=["This is an introduction."],
        editorial_note=["Note for editors."]
    )
    
    turtle = concept.to_rdf(format="turtle")
    print("\nStatisticalConcept Turtle:")
    print(turtle)
    
    assert "xkos:disjoint" in turtle
    assert "xkos:broaderGeneric" in turtle
    assert "xkos:introduction" in turtle
    assert "xkos:editorialNote" in turtle

def test_statistical_classification_properties():
    """Test new properties on StatisticalClassification."""
    classification = StatisticalClassification(
        id="class1",
        succeeds=["http://example.com/class/old"],
        disjoint=["http://example.com/class/other"],
        change_note=["Changed in version 2."]
    )
    
    turtle = classification.to_rdf(format="turtle")
    print("\nStatisticalClassification Turtle:")
    print(turtle)
    
    assert "xkos:succeeds" in turtle
    assert "xkos:disjoint" in turtle
    assert "xkos:changeNote" in turtle

if __name__ == "__main__":
    test_classification_level_properties()
    test_statistical_concept_properties()
    test_statistical_classification_properties()
    print("\n✅ All XKOS expansion tests passed!")
