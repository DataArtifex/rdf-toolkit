"""Test DCMI Metadata Terms expansion."""

from dartfx.rdf.pydantic.dcterms import (
    DublinCoreRecord, BibliographicResource, Location, PeriodOfTime,
    RightsStatement, DCTERMS
)
from rdflib import URIRef

def test_bibliographic_resource():
    """Test BibliographicResource class."""
    bib = BibliographicResource(id="bib1")
    
    turtle = bib.to_rdf(format="turtle")
    print("BibliographicResource Turtle:")
    print(turtle)
    
    assert "dcterms:BibliographicResource" in turtle

def test_record_properties():
    """Test new properties on DublinCoreRecord."""
    
    location = Location(id="loc1")
    period = PeriodOfTime(id="period1")
    rights = RightsStatement(id="rights1")
    
    record = DublinCoreRecord(
        id="rec1",
        title="My Record",
        spatial=location,
        temporal=period,
        access_rights=rights,
        abstract="A short summary.",
        table_of_contents="Chapter 1..."
    )
    
    turtle = record.to_rdf(format="turtle")
    print("\nRecord Turtle:")
    print(turtle)
    
    assert "dcterms:spatial" in turtle
    assert "dcterms:temporal" in turtle
    assert "dcterms:accessRights" in turtle
    assert "dcterms:abstract" in turtle
    assert "dcterms:tableOfContents" in turtle

if __name__ == "__main__":
    test_bibliographic_resource()
    test_record_properties()
    print("\n✅ All DCMI expansion tests passed!")
