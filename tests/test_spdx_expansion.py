"""Test SPDX expansion."""

from dartfx.rdf.pydantic.spdx import (
    Snippet, File, Review, LicenseException, ConjunctiveLicenseSet,
    SpdxDocument, Package, SPDX
)
from rdflib import URIRef

def test_snippet():
    """Test Snippet class."""
    file = File(name=["foo.c"])
    snippet = Snippet(
        name=["Snippet 1"],
        snippet_from_file=[file],
        snippet_byte_range=["startPointer: 3100"],
        license_concluded=["http://spdx.org/licenses/MIT"]
    )
    
    turtle = snippet.to_rdf(format="turtle")
    print("Snippet Turtle:")
    print(turtle)
    
    assert "spdx:Snippet" in turtle
    assert "spdx:snippetFromFile" in turtle
    assert "spdx:licenseConcluded" in turtle

def test_review():
    """Test Review class."""
    review = Review(
        reviewer=["Person: Alice"],
        comment=["Looks good."]
    )
    
    turtle = review.to_rdf(format="turtle")
    print("\nReview Turtle:")
    print(turtle)
    
    assert "spdx:Review" in turtle
    assert "spdx:reviewer" in turtle
    assert "Alice" in turtle

def test_license_set():
    """Test License Set."""
    license_set = ConjunctiveLicenseSet(
        member=["http://spdx.org/licenses/MIT", "http://spdx.org/licenses/Apache-2.0"]
    )
    
    turtle = license_set.to_rdf(format="turtle")
    print("\nLicense Set Turtle:")
    print(turtle)
    
    assert "spdx:ConjunctiveLicenseSet" in turtle
    assert "spdx:member" in turtle

def test_package_purpose():
    """Test Package primaryPackagePurpose."""
    package = Package(
        name=["MyLib"],
        primary_package_purpose=["LIBRARY"]
    )
    
    turtle = package.to_rdf(format="turtle")
    print("\nPackage Turtle:")
    print(turtle)
    
    assert "spdx:primaryPackagePurpose" in turtle
    assert "LIBRARY" in turtle

if __name__ == "__main__":
    test_snippet()
    test_review()
    test_license_set()
    test_package_purpose()
    print("\n✅ All SPDX expansion tests passed!")
