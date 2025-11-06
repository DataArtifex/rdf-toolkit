"""Test pydantic_dcterms module."""

from datetime import datetime
from dartfx.rdf.pydantic_dcterms import DublinCoreRecord, Agent, DcmiFrequency


def test_basic_dublin_core_record():
    """Test creating a basic Dublin Core record."""
    record = DublinCoreRecord(
        id="example-dataset",
        title="Example Dataset",
        description="This is an example dataset for testing.",
        creator="https://example.org/people/john-doe",
        created=datetime(2024, 1, 1, 12, 0, 0),
        language="en",
        subject=["testing", "example"],
    )
    
    # Test serialization to Turtle
    turtle = record.to_rdf(format="turtle")
    print("Turtle output:")
    print(turtle)
    print()
    
    # Test round-trip
    restored = DublinCoreRecord.from_rdf(turtle, format="turtle")
    assert restored.id == record.id
    assert restored.title == record.title
    assert restored.description == record.description
    print("✓ Basic record round-trip successful")


def test_agent():
    """Test creating an Agent resource."""
    agent = Agent(
        id="john-doe",
        name="John Doe"
    )
    
    turtle = agent.to_rdf(format="turtle")
    print("Agent Turtle output:")
    print(turtle)
    print()
    
    # Test round-trip
    restored = Agent.from_rdf(turtle, format="turtle")
    assert restored.id == agent.id
    assert restored.name == agent.name
    print("✓ Agent round-trip successful")


def test_frequency_enum():
    """Test using DcmiFrequency enum."""
    record = DublinCoreRecord(
        id="periodic-collection",
        title="Monthly Publication",
        accrual_periodicity=DcmiFrequency.MONTHLY,
    )
    
    turtle = record.to_rdf(format="turtle")
    print("Frequency Turtle output:")
    print(turtle)
    print()
    
    # Verify the frequency value is in the output
    assert DcmiFrequency.MONTHLY.value in turtle
    print("✓ Frequency enum serialization successful")


if __name__ == "__main__":
    test_basic_dublin_core_record()
    test_agent()
    test_frequency_enum()
    print("\n✅ All tests passed!")
