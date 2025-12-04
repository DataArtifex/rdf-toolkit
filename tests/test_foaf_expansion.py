"""Test expanded FOAF vocabulary."""

from dartfx.rdf.pydantic.foaf import (
    Person, Project, OnlineChatAccount, PersonalProfileDocument, Agent, FOAF
)
from rdflib import URIRef

def test_expanded_person_properties():
    """Test new properties on Person."""
    person = Person(
        name=["Alice"],
        geekcode=["GEEK123"],
        myers_briggs=["INTJ"],
        plan=["To take over the world"],
        dna_checksum=["sha1:1234567890"],
        workplace_homepage=["http://example.org/work"],
        school_homepage=["http://example.org/school"],
        last_name=["Smith"]
    )
    
    turtle = person.to_rdf(format="turtle")
    print("Person Turtle:")
    print(turtle)
    
    assert "foaf:geekcode" in turtle
    assert "GEEK123" in turtle
    assert "foaf:myersBriggs" in turtle
    assert "INTJ" in turtle
    assert "foaf:lastName" in turtle
    assert "Smith" in turtle

def test_project():
    """Test Project class and properties."""
    project = Project(
        name=["Project X"],
        homepage=["http://example.org/project-x"],
        funded_by=["http://example.org/funder"]
    )
    
    turtle = project.to_rdf(format="turtle")
    print("\nProject Turtle:")
    print(turtle)
    
    assert "foaf:Project" in turtle
    assert "foaf:name" in turtle
    assert "Project X" in turtle
    assert "foaf:fundedBy" in turtle

def test_online_chat_account():
    """Test OnlineChatAccount."""
    account = OnlineChatAccount(
        account_name=["alice_chat"],
        account_service_homepage=["http://chat.example.org"]
    )
    
    turtle = account.to_rdf(format="turtle")
    print("\nChat Account Turtle:")
    print(turtle)
    
    assert "foaf:OnlineChatAccount" in turtle
    assert "foaf:accountName" in turtle
    assert "alice_chat" in turtle

def test_agent_chat_ids():
    """Test chat ID properties on Agent."""
    agent = Agent(
        name=["Bob"],
        aim_chat_id=["bob_aim"],
        jabber_id=["bob@jabber.org"]
    )
    
    turtle = agent.to_rdf(format="turtle")
    print("\nAgent Turtle:")
    print(turtle)
    
    assert "foaf:aimChatID" in turtle
    assert "bob_aim" in turtle
    assert "foaf:jabberID" in turtle
    assert "bob@jabber.org" in turtle

if __name__ == "__main__":
    test_expanded_person_properties()
    test_project()
    test_online_chat_account()
    test_agent_chat_ids()
    print("\n✅ All FOAF expansion tests passed!")
