"""Test ODRL expansion."""

from dartfx.rdf.pydantic.odrl import (
    Privacy, Ticket, Assertion, Request, ConflictTerm, Permission, ODRL2
)
from rdflib import URIRef

def test_privacy_policy():
    """Test Privacy Policy class."""
    privacy = Privacy(uid=["http://example.com/policy:1010"])
    
    turtle = privacy.to_rdf(format="turtle")
    print("Privacy Policy Turtle:")
    print(turtle)
    
    assert "odrl:Privacy" in turtle
    assert "http://example.com/policy:1010" in turtle

def test_conflict_term():
    """Test ConflictTerm and conflict property."""
    conflict = ConflictTerm(uid=["http://www.w3.org/ns/odrl/2/perm"])
    
    policy = Privacy(
        uid=["http://example.com/policy:1011"],
        conflict=[conflict]
    )
    
    turtle = policy.to_rdf(format="turtle")
    print("\nPolicy with Conflict Turtle:")
    print(turtle)
    
    assert "odrl:conflict" in turtle
    assert "odrl:ConflictTerm" in turtle

def test_rule_failure():
    """Test failure property on Rule."""
    fail_rule = Permission(uid=["http://example.com/rule:fail"])
    perm = Permission(
        uid=["http://example.com/rule:1"],
        failure=[fail_rule]
    )
    
    turtle = perm.to_rdf(format="turtle")
    print("\nPermission with Failure Turtle:")
    print(turtle)
    
    assert "odrl:failure" in turtle

if __name__ == "__main__":
    test_privacy_policy()
    test_conflict_term()
    test_rule_failure()
    print("\n✅ All ODRL expansion tests passed!")
