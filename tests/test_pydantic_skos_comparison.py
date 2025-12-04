"""Example showing the benefits of pydantic_skos over the old skos implementation."""

from dartfx.rdf.pydantic.skos import Concept, ConceptScheme


def demonstrate_pydantic_skos():
    """Demonstrate the clean Pydantic-based SKOS API."""
    
    print("=" * 70)
    print("Pydantic SKOS Example")
    print("=" * 70)
    
    # Create a concept scheme
    scheme = ConceptScheme(
        id="taxonomy",
        pref_label=["Biological Taxonomy"],
        definition=["A hierarchical classification of living organisms"],
    )
    
    # Create concepts with relationships
    animalia = Concept(
        id="animalia",
        pref_label=["Animalia", "Animal Kingdom"],
        definition=["A kingdom of living organisms"],
        in_scheme=[scheme],
    )
    
    mammalia = Concept(
        id="mammalia",
        pref_label=["Mammalia", "Mammals"],
        alt_label=["Mammalian"],
        definition=["Warm-blooded vertebrates with hair or fur"],
        broader=["http://example.org/animalia"],
        in_scheme=[scheme],
    )
    
    felidae = Concept(
        id="felidae",
        pref_label=["Felidae", "Cat Family"],
        definition=["A family of mammals in the order Carnivora"],
        broader=["http://example.org/mammalia"],
        narrower=[
            "http://example.org/felis",
            "http://example.org/panthera"
        ],
    )
    
    # Serialize to RDF
    print("\n1. ConceptScheme:")
    print(scheme.to_rdf(format="turtle"))
    
    print("\n2. Concept with broader relationships:")
    print(mammalia.to_rdf(format="turtle"))
    
    print("\n3. Concept with broader and narrower relationships:")
    print(felidae.to_rdf(format="turtle"))
    
    # Demonstrate type safety and validation
    print("\n4. Benefits:")
    print("   ✓ Type-safe field definitions with Pydantic validation")
    print("   ✓ Automatic serialization to any RDF format (Turtle, XML, JSON-LD, etc.)")
    print("   ✓ Deserialization from RDF back to Python objects")
    print("   ✓ IDE autocomplete and type checking")
    print("   ✓ Clean, Pythonic API")
    print("   ✓ Support for nested relationships and collections")
    
    # Round-trip demonstration
    turtle = felidae.to_rdf(format="turtle")
    restored = Concept.from_rdf(turtle, format="turtle")
    print(f"\n5. Round-trip verification: {restored.id == felidae.id}")
    print(f"   Restored pref_label: {restored.pref_label}")
    print(f"   Restored definition: {restored.definition}")
    

if __name__ == "__main__":
    demonstrate_pydantic_skos()
