"""Test pydantic_skos module."""

from dartfx.rdf.pydantic.skos import ConceptScheme, Concept, Collection


def test_concept_scheme():
    """Test creating a SKOS Concept Scheme."""
    scheme = ConceptScheme(
        id="animals",
        pref_label=["Animals", "Animaux"],
        definition=["A classification scheme for animals"],
    )
    
    # Test serialization to Turtle
    turtle = scheme.to_rdf(format="turtle")
    print("ConceptScheme Turtle output:")
    print(turtle)
    print()
    
    # Verify the output contains expected elements
    assert "skos:ConceptScheme" in turtle
    assert "skos:prefLabel" in turtle
    assert "Animals" in turtle
    
    # Test round-trip
    restored = ConceptScheme.from_rdf(turtle, format="turtle")
    assert restored.id == scheme.id
    assert restored.pref_label == scheme.pref_label
    print("✓ ConceptScheme round-trip successful")


def test_concept():
    """Test creating a SKOS Concept."""
    concept = Concept(
        id="cat",
        pref_label=["Cat", "Chat"],
        alt_label=["Feline", "Kitty"],
        definition=["A small domesticated carnivorous mammal"],
        notation=["C001"],
    )
    
    turtle = concept.to_rdf(format="turtle")
    print("Concept Turtle output:")
    print(turtle)
    print()
    
    # Verify the output
    assert "skos:Concept" in turtle
    assert "skos:prefLabel" in turtle
    assert "Cat" in turtle
    assert "skos:altLabel" in turtle
    assert "skos:definition" in turtle
    
    # Test round-trip
    restored = Concept.from_rdf(turtle, format="turtle")
    assert restored.id == concept.id
    assert restored.pref_label == concept.pref_label
    assert restored.alt_label == concept.alt_label
    print("✓ Concept round-trip successful")


def test_concept_with_relationships():
    """Test creating concepts with hierarchical relationships."""
    # Create a broader concept
    animal = Concept(
        id="animal",
        pref_label=["Animal"],
        definition=["A living organism that feeds on organic matter"],
    )
    
    # Create a narrower concept
    mammal = Concept(
        id="mammal",
        pref_label=["Mammal"],
        definition=["A warm-blooded vertebrate animal"],
        broader=["http://example.org/animal"],  # Reference to broader concept
    )
    
    turtle = mammal.to_rdf(format="turtle")
    print("Concept with relationships Turtle output:")
    print(turtle)
    print()
    
    assert "skos:broader" in turtle
    assert "http://example.org/animal" in turtle
    print("✓ Concept with relationships serialization successful")


def test_collection():
    """Test creating a SKOS Collection."""
    collection = Collection(
        id="domestic-animals",
        pref_label=["Domestic Animals"],
        member=["http://example.org/cat", "http://example.org/dog"],
    )
    
    turtle = collection.to_rdf(format="turtle")
    print("Collection Turtle output:")
    print(turtle)
    print()
    
    assert "skos:Collection" in turtle
    assert "skos:member" in turtle
    print("✓ Collection serialization successful")


if __name__ == "__main__":
    test_concept_scheme()
    test_concept()
    test_concept_with_relationships()
    test_collection()
    print("\n✅ All tests passed!")
