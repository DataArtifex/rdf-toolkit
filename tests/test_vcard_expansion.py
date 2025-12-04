"""Test vCard expansion."""

from dartfx.rdf.pydantic.vcard import (
    Individual, Gender, Friend, Acquaintance, VCARD
)
from rdflib import URIRef

def test_gender():
    """Test Gender class."""
    gender = Gender(sex=["Female"], identity=["Non-binary"])
    
    person = Individual(
        fn=["Alice"],
        has_gender=[gender]
    )
    
    turtle = person.to_rdf(format="turtle")
    print("Gender Turtle:")
    print(turtle)
    
    assert "vcard:Gender" in turtle
    assert "vcard:sex" in turtle
    assert "Female" in turtle
    assert "vcard:hasGender" in turtle

def test_related():
    """Test Related classes."""
    bob = Individual(fn=["Bob"])
    alice = Individual(fn=["Alice"])
    
    friendship = Friend(has_value=[bob])
    alice.has_related = [friendship]
    
    turtle = alice.to_rdf(format="turtle")
    print("\nRelated Turtle:")
    print(turtle)
    
    assert "vcard:Friend" in turtle
    assert "vcard:hasValue" in turtle
    assert "vcard:hasRelated" in turtle

def test_acquaintance():
    """Test Acquaintance class."""
    charlie = Individual(fn=["Charlie"])
    alice = Individual(fn=["Alice"])
    
    acq = Acquaintance(has_value=[charlie])
    alice.has_related = [acq]
    
    turtle = alice.to_rdf(format="turtle")
    print("\nAcquaintance Turtle:")
    print(turtle)
    
    assert "vcard:Acquaintance" in turtle

if __name__ == "__main__":
    test_gender()
    test_related()
    test_acquaintance()
    print("\n✅ All vCard expansion tests passed!")
