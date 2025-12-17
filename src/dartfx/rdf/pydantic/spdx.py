"""SPDX (Software Package Data Exchange) vocabulary using Pydantic RDF models.

This module provides Pydantic-based models for the SPDX vocabulary,
allowing easy serialization to and from RDF formats.

References:
- https://spdx.github.io/spdx-spec/
- https://spdx.org/rdf/terms/

"""

from __future__ import annotations
from typing import Annotated, List, Optional
from datetime import datetime

from rdflib import Namespace, URIRef

from ._base import RdfBaseModel, RdfProperty


# SPDX namespace (not built-in to rdflib)
SPDX = Namespace("http://spdx.org/rdf/terms#")


class SpdxResource(RdfBaseModel):
    """Base class for SPDX resources."""
    
    rdf_namespace = SPDX
    rdf_prefixes = {"spdx": SPDX}


class SpdxDocument(SpdxResource):
    """An SPDX Document."""
    
    rdf_type: str = str(SPDX.SpdxDocument)
    
    # Document properties
    spdx_version: Annotated[Optional[List[str]], RdfProperty(SPDX.spdxVersion)] = None
    data_license: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.dataLicense)] = None
    name: Annotated[Optional[List[str]], RdfProperty(SPDX.name)] = None
    document_namespace: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.documentNamespace)] = None
    
    # Creation info
    creation_info: Annotated[Optional[List[str | URIRef | CreationInfo]], RdfProperty(SPDX.creationInfo)] = None
    
    # External references
    external_document_ref: Annotated[Optional[List[str | URIRef | ExternalDocumentRef]], RdfProperty(SPDX.externalDocumentRef)] = None
    
    # Describes
    describes_package: Annotated[Optional[List[str | URIRef | Package]], RdfProperty(SPDX.describesPackage)] = None
    
    # Relationships
    relationship: Annotated[Optional[List[str | URIRef | Relationship]], RdfProperty(SPDX.relationship)] = None
    
    # Annotations
    annotation: Annotated[Optional[List[str | URIRef | Annotation]], RdfProperty(SPDX.annotation)] = None
    
    # Comment
    comment: Annotated[Optional[List[str]], RdfProperty(SPDX.comment)] = None


class CreationInfo(SpdxResource):
    """SPDX Creation Info."""
    
    rdf_type: str = str(SPDX.CreationInfo)
    
    created: Annotated[Optional[List[str | datetime]], RdfProperty(SPDX.created)] = None
    creator: Annotated[Optional[List[str]], RdfProperty(SPDX.creator)] = None
    license_list_version: Annotated[Optional[List[str]], RdfProperty(SPDX.licenseListVersion)] = None
    comment: Annotated[Optional[List[str]], RdfProperty(SPDX.comment)] = None


class Package(SpdxResource):
    """An SPDX Package."""
    
    rdf_type: str = str(SPDX.Package)
    
    # Basic info
    name: Annotated[Optional[List[str]], RdfProperty(SPDX.name)] = None
    version_info: Annotated[Optional[List[str]], RdfProperty(SPDX.versionInfo)] = None
    package_file_name: Annotated[Optional[List[str]], RdfProperty(SPDX.packageFileName)] = None
    supplier: Annotated[Optional[List[str]], RdfProperty(SPDX.supplier)] = None
    originator: Annotated[Optional[List[str]], RdfProperty(SPDX.originator)] = None
    download_location: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.downloadLocation)] = None
    
    # Verification
    package_verification_code: Annotated[Optional[List[str | URIRef | PackageVerificationCode]], RdfProperty(SPDX.packageVerificationCode)] = None
    checksum: Annotated[Optional[List[str | URIRef | Checksum]], RdfProperty(SPDX.checksum)] = None
    
    # Homepage
    homepage: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.homepage)] = None
    
    # Source info
    source_info: Annotated[Optional[List[str]], RdfProperty(SPDX.sourceInfo)] = None
    
    # License info
    license_concluded: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.licenseConcluded)] = None
    license_info_from_files: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.licenseInfoFromFiles)] = None
    license_declared: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.licenseDeclared)] = None
    license_comments: Annotated[Optional[List[str]], RdfProperty(SPDX.licenseComments)] = None
    copyright_text: Annotated[Optional[List[str]], RdfProperty(SPDX.copyrightText)] = None
    
    # Summary and description
    summary: Annotated[Optional[List[str]], RdfProperty(SPDX.summary)] = None
    description: Annotated[Optional[List[str]], RdfProperty(SPDX.description)] = None
    comment: Annotated[Optional[List[str]], RdfProperty(SPDX.comment)] = None
    
    # External references
    external_ref: Annotated[Optional[List[str | URIRef | ExternalRef]], RdfProperty(SPDX.externalRef)] = None
    
    # Files
    has_file: Annotated[Optional[List[str | URIRef | File]], RdfProperty(SPDX.hasFile)] = None
    
    # Attribution
    attribution_text: Annotated[Optional[List[str]], RdfProperty(SPDX.attributionText)] = None
    
    # Other
    primary_package_purpose: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.primaryPackagePurpose)] = None


class File(SpdxResource):
    """An SPDX File."""
    
    rdf_type: str = str(SPDX.File)
    
    # Basic info
    file_name: Annotated[Optional[List[str]], RdfProperty(SPDX.fileName)] = None
    file_type: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.fileType)] = None
    
    # Checksums
    checksum: Annotated[Optional[List[str | URIRef | Checksum]], RdfProperty(SPDX.checksum)] = None
    
    # License info
    license_concluded: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.licenseConcluded)] = None
    license_info_in_file: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.licenseInfoInFile)] = None
    license_comments: Annotated[Optional[List[str]], RdfProperty(SPDX.licenseComments)] = None
    copyright_text: Annotated[Optional[List[str]], RdfProperty(SPDX.copyrightText)] = None
    
    # Notices
    notice_text: Annotated[Optional[List[str]], RdfProperty(SPDX.noticeText)] = None
    comment: Annotated[Optional[List[str]], RdfProperty(SPDX.comment)] = None
    
    # Attribution
    attribution_text: Annotated[Optional[List[str]], RdfProperty(SPDX.attributionText)] = None
    
    # Contributors
    file_contributor: Annotated[Optional[List[str]], RdfProperty(SPDX.fileContributor)] = None
    
    # Deprecated properties
    file_dependency: Annotated[Optional[List[str | URIRef | File]], RdfProperty(SPDX.fileDependency)] = None
    artifact_of: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.artifactOf)] = None


class Checksum(SpdxResource):
    """An SPDX Checksum."""
    
    rdf_type: str = str(SPDX.Checksum)
    
    algorithm: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.algorithm)] = None
    checksum_value: Annotated[Optional[List[str]], RdfProperty(SPDX.checksumValue)] = None


class PackageVerificationCode(SpdxResource):
    """An SPDX Package Verification Code."""
    
    rdf_type: str = str(SPDX.PackageVerificationCode)
    
    package_verification_code_value: Annotated[Optional[List[str]], RdfProperty(SPDX.packageVerificationCodeValue)] = None
    package_verification_code_excluded_file: Annotated[Optional[List[str]], RdfProperty(SPDX.packageVerificationCodeExcludedFile)] = None


class Relationship(SpdxResource):
    """An SPDX Relationship."""
    
    rdf_type: str = str(SPDX.Relationship)
    
    relationship_type: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.relationshipType)] = None
    related_spdx_element: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.relatedSpdxElement)] = None
    comment: Annotated[Optional[List[str]], RdfProperty(SPDX.comment)] = None


class Annotation(SpdxResource):
    """An SPDX Annotation."""
    
    rdf_type: str = str(SPDX.Annotation)
    
    annotator: Annotated[Optional[List[str]], RdfProperty(SPDX.annotator)] = None
    annotation_date: Annotated[Optional[List[str | datetime]], RdfProperty(SPDX.annotationDate)] = None
    annotation_type: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.annotationType)] = None
    comment: Annotated[Optional[List[str]], RdfProperty(SPDX.comment)] = None


class ExternalRef(SpdxResource):
    """An SPDX External Reference."""
    
    rdf_type: str = str(SPDX.ExternalRef)
    
    reference_category: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.referenceCategory)] = None
    reference_type: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.referenceType)] = None
    reference_locator: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.referenceLocator)] = None
    comment: Annotated[Optional[List[str]], RdfProperty(SPDX.comment)] = None


class ExternalDocumentRef(SpdxResource):
    """An SPDX External Document Reference."""
    
    rdf_type: str = str(SPDX.ExternalDocumentRef)
    
    external_document_id: Annotated[Optional[List[str]], RdfProperty(SPDX.externalDocumentId)] = None
    spdx_document: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.spdxDocument)] = None
    checksum: Annotated[Optional[List[str | URIRef | Checksum]], RdfProperty(SPDX.checksum)] = None


class License(SpdxResource):
    """Base class for SPDX Licenses."""
    
    license_id: Annotated[Optional[List[str]], RdfProperty(SPDX.licenseId)] = None
    name: Annotated[Optional[List[str]], RdfProperty(SPDX.name)] = None
    license_text: Annotated[Optional[List[str]], RdfProperty(SPDX.licenseText)] = None
    see_also: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.seeAlso)] = None
    comment: Annotated[Optional[List[str]], RdfProperty(SPDX.comment)] = None


class ExtractedLicensingInfo(License):
    """An SPDX Extracted Licensing Info."""
    
    rdf_type: str = str(SPDX.ExtractedLicensingInfo)


class Snippet(SpdxResource):
    """An SPDX Snippet."""
    
    rdf_type: str = str(SPDX.Snippet)
    
    snippet_from_file: Annotated[Optional[List[str | URIRef | File]], RdfProperty(SPDX.snippetFromFile)] = None
    snippet_byte_range: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.snippetByteRange)] = None
    snippet_line_range: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.snippetLineRange)] = None
    license_info_in_snippet: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.licenseInfoInSnippet)] = None
    license_concluded: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.licenseConcluded)] = None
    copyright_text: Annotated[Optional[List[str]], RdfProperty(SPDX.copyrightText)] = None
    comment: Annotated[Optional[List[str]], RdfProperty(SPDX.comment)] = None
    name: Annotated[Optional[List[str]], RdfProperty(SPDX.name)] = None


class Review(SpdxResource):
    """An SPDX Review."""
    
    rdf_type: str = str(SPDX.Review)
    
    reviewer: Annotated[Optional[List[str]], RdfProperty(SPDX.reviewer)] = None
    review_date: Annotated[Optional[List[str | datetime]], RdfProperty(SPDX.reviewDate)] = None
    comment: Annotated[Optional[List[str]], RdfProperty(SPDX.comment)] = None


class LicenseException(SpdxResource):
    """An SPDX License Exception."""
    
    rdf_type: str = str(SPDX.LicenseException)
    
    license_exception_id: Annotated[Optional[List[str]], RdfProperty(SPDX.licenseExceptionId)] = None
    name: Annotated[Optional[List[str]], RdfProperty(SPDX.name)] = None
    license_exception_text: Annotated[Optional[List[str]], RdfProperty(SPDX.licenseExceptionText)] = None
    license_exception_template: Annotated[Optional[List[str]], RdfProperty(SPDX.licenseExceptionTemplate)] = None
    see_also: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.seeAlso)] = None
    comment: Annotated[Optional[List[str]], RdfProperty(SPDX.comment)] = None


class SimpleLicensingInfo(License):
    """An SPDX Simple Licensing Info."""
    
    rdf_type: str = str(SPDX.SimpleLicensingInfo)


class OrLaterOperator(License):
    """An SPDX Or Later Operator."""
    
    rdf_type: str = str(SPDX.OrLaterOperator)
    
    member: Annotated[Optional[List[str | URIRef | License]], RdfProperty(SPDX.member)] = None


class WithExceptionOperator(License):
    """An SPDX With Exception Operator."""
    
    rdf_type: str = str(SPDX.WithExceptionOperator)
    
    member: Annotated[Optional[List[str | URIRef | License]], RdfProperty(SPDX.member)] = None
    license_exception: Annotated[Optional[List[str | URIRef | LicenseException]], RdfProperty(SPDX.licenseException)] = None


class ConjunctiveLicenseSet(License):
    """An SPDX Conjunctive License Set."""
    
    rdf_type: str = str(SPDX.ConjunctiveLicenseSet)
    
    member: Annotated[Optional[List[str | URIRef | License]], RdfProperty(SPDX.member)] = None


class DisjunctiveLicenseSet(License):
    """An SPDX Disjunctive License Set."""
    
    rdf_type: str = str(SPDX.DisjunctiveLicenseSet)
    
    member: Annotated[Optional[List[str | URIRef | License]], RdfProperty(SPDX.member)] = None


class ReferenceType(SpdxResource):
    """An SPDX Reference Type."""
    
    rdf_type: str = str(SPDX.ReferenceType)
    
    contextual_example: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.contextualExample)] = None
    external_reference_site: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.externalReferenceSite)] = None
    documentation: Annotated[Optional[List[str | URIRef]], RdfProperty(SPDX.documentation)] = None


class FileType(SpdxResource):
    """An SPDX File Type."""
    
    rdf_type: str = str(SPDX.FileType)


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


