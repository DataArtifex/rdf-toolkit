"""SPDX (Software Package Data Exchange) vocabulary using Pydantic RDF models.

This module provides Pydantic-based models for the SPDX vocabulary,
allowing easy serialization to and from RDF formats.

References:
- https://spdx.github.io/spdx-spec/
- https://spdx.org/rdf/terms/

"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, ClassVar

from rdflib import Namespace, URIRef

from ._base import RdfBaseModel, RdfProperty

# SPDX namespace (not built-in to rdflib)
SPDX = Namespace("http://spdx.org/rdf/terms#")


class SpdxResource(RdfBaseModel):
    """Base class for SPDX resources."""

    rdf_namespace: ClassVar = SPDX
    rdf_prefixes: ClassVar = {"spdx": SPDX}


class SpdxDocument(SpdxResource):
    """An SPDX Document."""

    rdf_type: ClassVar[str] = str(SPDX.SpdxDocument)

    # Document properties
    spdx_version: Annotated[list[str] | None, RdfProperty(SPDX.spdxVersion)] = None
    data_license: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.dataLicense)] = None
    name: Annotated[list[str] | None, RdfProperty(SPDX.name)] = None
    document_namespace: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.documentNamespace)] = None

    # Creation info
    creation_info: Annotated[list[str | URIRef | CreationInfo] | None, RdfProperty(SPDX.creationInfo)] = None

    # External references
    external_document_ref: Annotated[
        list[str | URIRef | ExternalDocumentRef] | None,
        RdfProperty(SPDX.externalDocumentRef),
    ] = None

    # Describes
    describes_package: Annotated[list[str | URIRef | Package] | None, RdfProperty(SPDX.describesPackage)] = None

    # Relationships
    relationship: Annotated[list[str | URIRef | Relationship] | None, RdfProperty(SPDX.relationship)] = None

    # Annotations
    annotation: Annotated[list[str | URIRef | Annotation] | None, RdfProperty(SPDX.annotation)] = None

    # Comment
    comment: Annotated[list[str] | None, RdfProperty(SPDX.comment)] = None


class CreationInfo(SpdxResource):
    """SPDX Creation Info."""

    rdf_type: ClassVar[str] = str(SPDX.CreationInfo)

    created: Annotated[list[str | datetime] | None, RdfProperty(SPDX.created)] = None
    creator: Annotated[list[str] | None, RdfProperty(SPDX.creator)] = None
    license_list_version: Annotated[list[str] | None, RdfProperty(SPDX.licenseListVersion)] = None
    comment: Annotated[list[str] | None, RdfProperty(SPDX.comment)] = None


class Package(SpdxResource):
    """An SPDX Package."""

    rdf_type: ClassVar[str] = str(SPDX.Package)

    # Basic info
    name: Annotated[list[str] | None, RdfProperty(SPDX.name)] = None
    version_info: Annotated[list[str] | None, RdfProperty(SPDX.versionInfo)] = None
    package_file_name: Annotated[list[str] | None, RdfProperty(SPDX.packageFileName)] = None
    supplier: Annotated[list[str] | None, RdfProperty(SPDX.supplier)] = None
    originator: Annotated[list[str] | None, RdfProperty(SPDX.originator)] = None
    download_location: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.downloadLocation)] = None

    # Verification
    package_verification_code: Annotated[
        list[str | URIRef | PackageVerificationCode] | None,
        RdfProperty(SPDX.packageVerificationCode),
    ] = None
    checksum: Annotated[list[str | URIRef | Checksum] | None, RdfProperty(SPDX.checksum)] = None

    # Homepage
    homepage: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.homepage)] = None

    # Source info
    source_info: Annotated[list[str] | None, RdfProperty(SPDX.sourceInfo)] = None

    # License info
    license_concluded: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.licenseConcluded)] = None
    license_info_from_files: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.licenseInfoFromFiles)] = None
    license_declared: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.licenseDeclared)] = None
    license_comments: Annotated[list[str] | None, RdfProperty(SPDX.licenseComments)] = None
    copyright_text: Annotated[list[str] | None, RdfProperty(SPDX.copyrightText)] = None

    # Summary and description
    summary: Annotated[list[str] | None, RdfProperty(SPDX.summary)] = None
    description: Annotated[list[str] | None, RdfProperty(SPDX.description)] = None
    comment: Annotated[list[str] | None, RdfProperty(SPDX.comment)] = None

    # External references
    external_ref: Annotated[list[str | URIRef | ExternalRef] | None, RdfProperty(SPDX.externalRef)] = None

    # Files
    has_file: Annotated[list[str | URIRef | File] | None, RdfProperty(SPDX.hasFile)] = None

    # Attribution
    attribution_text: Annotated[list[str] | None, RdfProperty(SPDX.attributionText)] = None

    # Other
    primary_package_purpose: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.primaryPackagePurpose)] = None


class File(SpdxResource):
    """An SPDX File."""

    rdf_type: ClassVar[str] = str(SPDX.File)

    # Basic info
    file_name: Annotated[list[str] | None, RdfProperty(SPDX.fileName)] = None
    file_type: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.fileType)] = None

    # Checksums
    checksum: Annotated[list[str | URIRef | Checksum] | None, RdfProperty(SPDX.checksum)] = None

    # License info
    license_concluded: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.licenseConcluded)] = None
    license_info_in_file: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.licenseInfoInFile)] = None
    license_comments: Annotated[list[str] | None, RdfProperty(SPDX.licenseComments)] = None
    copyright_text: Annotated[list[str] | None, RdfProperty(SPDX.copyrightText)] = None

    # Notices
    notice_text: Annotated[list[str] | None, RdfProperty(SPDX.noticeText)] = None
    comment: Annotated[list[str] | None, RdfProperty(SPDX.comment)] = None

    # Attribution
    attribution_text: Annotated[list[str] | None, RdfProperty(SPDX.attributionText)] = None

    # Contributors
    file_contributor: Annotated[list[str] | None, RdfProperty(SPDX.fileContributor)] = None

    # Deprecated properties
    file_dependency: Annotated[list[str | URIRef | File] | None, RdfProperty(SPDX.fileDependency)] = None
    artifact_of: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.artifactOf)] = None


class Checksum(SpdxResource):
    """An SPDX Checksum."""

    rdf_type: ClassVar[str] = str(SPDX.Checksum)

    algorithm: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.algorithm)] = None
    checksum_value: Annotated[list[str] | None, RdfProperty(SPDX.checksumValue)] = None


class PackageVerificationCode(SpdxResource):
    """An SPDX Package Verification Code."""

    rdf_type: ClassVar[str] = str(SPDX.PackageVerificationCode)

    package_verification_code_value: Annotated[list[str] | None, RdfProperty(SPDX.packageVerificationCodeValue)] = None
    package_verification_code_excluded_file: Annotated[
        list[str] | None, RdfProperty(SPDX.packageVerificationCodeExcludedFile)
    ] = None


class Relationship(SpdxResource):
    """An SPDX Relationship."""

    rdf_type: ClassVar[str] = str(SPDX.Relationship)

    relationship_type: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.relationshipType)] = None
    related_spdx_element: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.relatedSpdxElement)] = None
    comment: Annotated[list[str] | None, RdfProperty(SPDX.comment)] = None


class Annotation(SpdxResource):
    """An SPDX Annotation."""

    rdf_type: ClassVar[str] = str(SPDX.Annotation)

    annotator: Annotated[list[str] | None, RdfProperty(SPDX.annotator)] = None
    annotation_date: Annotated[list[str | datetime] | None, RdfProperty(SPDX.annotationDate)] = None
    annotation_type: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.annotationType)] = None
    comment: Annotated[list[str] | None, RdfProperty(SPDX.comment)] = None


class ExternalRef(SpdxResource):
    """An SPDX External Reference."""

    rdf_type: ClassVar[str] = str(SPDX.ExternalRef)

    reference_category: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.referenceCategory)] = None
    reference_type: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.referenceType)] = None
    reference_locator: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.referenceLocator)] = None
    comment: Annotated[list[str] | None, RdfProperty(SPDX.comment)] = None


class ExternalDocumentRef(SpdxResource):
    """An SPDX External Document Reference."""

    rdf_type: ClassVar[str] = str(SPDX.ExternalDocumentRef)

    external_document_id: Annotated[list[str] | None, RdfProperty(SPDX.externalDocumentId)] = None
    spdx_document: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.spdxDocument)] = None
    checksum: Annotated[list[str | URIRef | Checksum] | None, RdfProperty(SPDX.checksum)] = None


class License(SpdxResource):
    """Base class for SPDX Licenses."""

    license_id: Annotated[list[str] | None, RdfProperty(SPDX.licenseId)] = None
    name: Annotated[list[str] | None, RdfProperty(SPDX.name)] = None
    license_text: Annotated[list[str] | None, RdfProperty(SPDX.licenseText)] = None
    see_also: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.seeAlso)] = None
    comment: Annotated[list[str] | None, RdfProperty(SPDX.comment)] = None


class ExtractedLicensingInfo(License):
    """An SPDX Extracted Licensing Info."""

    rdf_type: ClassVar[str] = str(SPDX.ExtractedLicensingInfo)


class Snippet(SpdxResource):
    """An SPDX Snippet."""

    rdf_type: ClassVar[str] = str(SPDX.Snippet)

    snippet_from_file: Annotated[list[str | URIRef | File] | None, RdfProperty(SPDX.snippetFromFile)] = None
    snippet_byte_range: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.snippetByteRange)] = None
    snippet_line_range: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.snippetLineRange)] = None
    license_info_in_snippet: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.licenseInfoInSnippet)] = None
    license_concluded: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.licenseConcluded)] = None
    copyright_text: Annotated[list[str] | None, RdfProperty(SPDX.copyrightText)] = None
    comment: Annotated[list[str] | None, RdfProperty(SPDX.comment)] = None
    name: Annotated[list[str] | None, RdfProperty(SPDX.name)] = None


class Review(SpdxResource):
    """An SPDX Review."""

    rdf_type: ClassVar[str] = str(SPDX.Review)

    reviewer: Annotated[list[str] | None, RdfProperty(SPDX.reviewer)] = None
    review_date: Annotated[list[str | datetime] | None, RdfProperty(SPDX.reviewDate)] = None
    comment: Annotated[list[str] | None, RdfProperty(SPDX.comment)] = None


class LicenseException(SpdxResource):
    """An SPDX License Exception."""

    rdf_type: ClassVar[str] = str(SPDX.LicenseException)

    license_exception_id: Annotated[list[str] | None, RdfProperty(SPDX.licenseExceptionId)] = None
    name: Annotated[list[str] | None, RdfProperty(SPDX.name)] = None
    license_exception_text: Annotated[list[str] | None, RdfProperty(SPDX.licenseExceptionText)] = None
    license_exception_template: Annotated[list[str] | None, RdfProperty(SPDX.licenseExceptionTemplate)] = None
    see_also: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.seeAlso)] = None
    comment: Annotated[list[str] | None, RdfProperty(SPDX.comment)] = None


class SimpleLicensingInfo(License):
    """An SPDX Simple Licensing Info."""

    rdf_type: ClassVar[str] = str(SPDX.SimpleLicensingInfo)


class OrLaterOperator(License):
    """An SPDX Or Later Operator."""

    rdf_type: ClassVar[str] = str(SPDX.OrLaterOperator)

    member: Annotated[list[str | URIRef | License] | None, RdfProperty(SPDX.member)] = None


class WithExceptionOperator(License):
    """An SPDX With Exception Operator."""

    rdf_type: ClassVar[str] = str(SPDX.WithExceptionOperator)

    member: Annotated[list[str | URIRef | License] | None, RdfProperty(SPDX.member)] = None
    license_exception: Annotated[list[str | URIRef | LicenseException] | None, RdfProperty(SPDX.licenseException)] = (
        None
    )


class ConjunctiveLicenseSet(License):
    """An SPDX Conjunctive License Set."""

    rdf_type: ClassVar[str] = str(SPDX.ConjunctiveLicenseSet)

    member: Annotated[list[str | URIRef | License] | None, RdfProperty(SPDX.member)] = None


class DisjunctiveLicenseSet(License):
    """An SPDX Disjunctive License Set."""

    rdf_type: ClassVar[str] = str(SPDX.DisjunctiveLicenseSet)

    member: Annotated[list[str | URIRef | License] | None, RdfProperty(SPDX.member)] = None


class ReferenceType(SpdxResource):
    """An SPDX Reference Type."""

    rdf_type: ClassVar[str] = str(SPDX.ReferenceType)

    contextual_example: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.contextualExample)] = None
    external_reference_site: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.externalReferenceSite)] = None
    documentation: Annotated[list[str | URIRef] | None, RdfProperty(SPDX.documentation)] = None


class FileType(SpdxResource):
    """An SPDX File Type."""

    rdf_type: ClassVar[str] = str(SPDX.FileType)


__all__ = [
    "SpdxResource",
    "SpdxDocument",
    "CreationInfo",
    "Package",
    "File",
    "Checksum",
    "PackageVerificationCode",
    "Relationship",
    "Annotation",
    "ExternalRef",
    "ExternalDocumentRef",
    "License",
    "ExtractedLicensingInfo",
    "Snippet",
    "Review",
    "LicenseException",
    "SimpleLicensingInfo",
    "OrLaterOperator",
    "WithExceptionOperator",
    "ConjunctiveLicenseSet",
    "DisjunctiveLicenseSet",
    "ReferenceType",
    "FileType",
]
