"""Test all pydantic RDF vocabulary modules."""

# Test FOAF
print("=" * 70)
print("Testing FOAF")
print("=" * 70)
from dartfx.rdf.pydantic_foaf import Person

person = Person(
    name=["John Doe"],
    given_name=["John"],
    family_name=["Doe"],
    mbox=["mailto:john@example.org"],
    homepage=["http://johndoe.com"]
)

print("Person Turtle output:")
print(person.to_rdf("turtle"))
print()

# Test ODRL
print("=" * 70)
print("Testing ODRL")
print("=" * 70)
from dartfx.rdf.pydantic_odrl import Policy

policy = Policy(
    uid=["http://example.org/policy1"]
)

print("Policy Turtle output:")
print(policy.to_rdf("turtle"))
print()

# Test PROV
print("=" * 70)
print("Testing PROV")
print("=" * 70)
from dartfx.rdf.pydantic_prov import Entity, Activity

entity = Entity(
    value=["Some data"]
)

activity = Activity(
    used=["http://example.org/entity1"]
)

print("Entity Turtle output:")
print(entity.to_rdf("turtle"))
print()

print("Activity Turtle output:")
print(activity.to_rdf("turtle"))
print()

# Test SPDX
print("=" * 70)
print("Testing SPDX")
print("=" * 70)
from dartfx.rdf.pydantic_spdx import Package, Checksum

checksum = Checksum(
    algorithm=["http://spdx.org/rdf/terms#checksumAlgorithm_sha1"],
    checksum_value=["da39a3ee5e6b4b0d3255bfef95601890afd80709"]
)

package = Package(
    name=["ExamplePackage"],
    version_info=["1.0.0"],
    download_location=["https://example.org/package.tar.gz"],
    checksum=[checksum]
)

print("Package Turtle output:")
print(package.to_rdf("turtle"))
print()

# Test VCARD
print("=" * 70)
print("Testing VCARD")
print("=" * 70)
from dartfx.rdf.pydantic_vcard import Individual, Name, Address

name = Name(
    given_name=["Jane"],
    family_name=["Smith"]
)

address = Address(
    street_address=["123 Main St"],
    locality=["Springfield"],
    region=["IL"],
    postal_code=["62701"],
    country_name=["USA"]
)

individual = Individual(
    fn=["Jane Smith"],
    n=[name],
    adr=[address]
)

print("Individual Turtle output:")
print(individual.to_rdf("turtle"))
print()

# Test XKOS
print("=" * 70)
print("Testing XKOS")
print("=" * 70)
from dartfx.rdf.pydantic_xkos import StatisticalClassification, ClassificationLevel

level = ClassificationLevel(
    depth=[1],
    pref_label=["Level 1"]
)

classification = StatisticalClassification(
    pref_label=["Statistical Classification"],
    definition=["A hierarchical classification system"],
    number_of_levels=[3]
)

print("Classification Level Turtle output:")
print(level.to_rdf("turtle"))
print()

print("Statistical Classification Turtle output:")
print(classification.to_rdf("turtle"))
print()

print("✅ All tests passed!")

