"""Test PROV expansion."""

from dartfx.rdf.pydantic.prov import (
    Entity, Activity, Agent, Influence, Location, EmptyCollection, PROV
)
from rdflib import URIRef

def test_influence():
    """Test Influence class and properties."""
    agent = Agent(id="agent1")
    influence = Influence(
        id="influence1",
        influencer=[agent]
    )
    
    entity = Entity(
        id="entity1",
        was_influenced_by=[influence]
    )
    
    turtle = entity.to_rdf(format="turtle")
    print("Entity with Influence Turtle:")
    print(turtle)
    
    assert "prov:Influence" in turtle
    assert "prov:wasInfluencedBy" in turtle
    assert "prov:influencer" in turtle

def test_location():
    """Test Location class and at_location property."""
    loc = Location(id="loc1")
    
    activity = Activity(
        id="act1",
        at_location=[loc]
    )
    
    turtle = activity.to_rdf(format="turtle")
    print("\nActivity with Location Turtle:")
    print(turtle)
    
    assert "prov:Location" in turtle
    assert "prov:atLocation" in turtle

def test_empty_collection():
    """Test EmptyCollection class."""
    coll = EmptyCollection(id="coll1")
    
    turtle = coll.to_rdf(format="turtle")
    print("\nEmptyCollection Turtle:")
    print(turtle)
    
    assert "prov:EmptyCollection" in turtle

if __name__ == "__main__":
    test_influence()
    test_location()
    test_empty_collection()
    print("\n✅ All PROV expansion tests passed!")
