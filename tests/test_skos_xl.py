"""Test SKOS-XL support."""

from dartfx.rdf.pydantic.skos import (
    Concept, ConceptScheme, Label, SKOSXL, SKOS
)
from rdflib import URIRef, Literal

def test_skos_xl_labels():
    """Test creating and linking SKOS-XL labels."""
    
    # Create a Label resource
    label = Label(
        id="label-1",
        literal_form="Big Cat"
    )
    
    # Create a Concept linking to the Label
    concept = Concept(
        id="cat",
        pref_label=["Cat"],
        pref_label_xl=[label]
    )
    
    turtle = concept.to_rdf(format="turtle")
    print("Concept with XL Label Turtle:")
    print(turtle)
    
    # Verify output
    assert "skosxl:Label" in turtle
    assert "skosxl:literalForm" in turtle
    assert "Big Cat" in turtle
    assert "skosxl:prefLabel" in turtle
    
    # Verify round-trip
    restored = Concept.from_rdf(turtle, format="turtle")
    assert restored.id == concept.id
    assert len(restored.pref_label_xl) == 1
    restored_label = restored.pref_label_xl[0]
    assert isinstance(restored_label, Label)
    assert restored_label.literal_form == "Big Cat"

def test_semantic_relations():
    """Test semantic and mapping relations."""
    c1 = Concept(id="c1", pref_label=["Concept 1"])
    c2 = Concept(id="c2", pref_label=["Concept 2"])
    
    c1.semantic_relation = [c2]
    c1.mapping_relation = ["http://example.org/external"]
    
    turtle = c1.to_rdf(format="turtle")
    print("\nConcept with Relations Turtle:")
    print(turtle)
    
    assert "skos:semanticRelation" in turtle
    assert "skos:mappingRelation" in turtle

if __name__ == "__main__":
    test_skos_xl_labels()
    test_semantic_relations()
    print("\n✅ All SKOS-XL tests passed!")
