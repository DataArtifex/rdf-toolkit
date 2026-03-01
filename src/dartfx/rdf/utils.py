import logging
import os
from typing import Any, cast

import pyshacl
from rdflib import RDF, Graph, Namespace


def shacl_validate(data: Graph | str | Any, shacl_path: str | os.PathLike[str]) -> tuple[bool, Graph, str]:
    """
    Validates an RDF graph against a SHACL shapes file.

    Args:
        data: The RDF graph to validate (rdflib.Graph, path to file, or dictionary of resources).
        shacl_path: Path to the SHACL shapes file (.ttl) used for validation.

    Returns:
        A tuple containing:
        - conforms (bool): True if the graph is valid, False otherwise.
        - results_graph (rdflib.Graph): The validation report graph.
        - results_text (str): The validation report as text.
    """

    if isinstance(data, str):
        g = Graph()
        g.parse(data)
    elif isinstance(data, Graph):
        g = data
    else:
        raise ValueError("Unsupported data type for validation. Expected Graph, file path, or resources dict.")

    logging.info(f"Validating graph against SHACL shapes: {shacl_path}")

    shacl_graph = Graph()
    shacl_graph.parse(str(shacl_path))

    conforms, results_graph, results_text = pyshacl.validate(
        data_graph=g, shacl_graph=shacl_graph, inference=None, serialize_report_graph=False
    )

    return cast(bool, conforms), cast(Graph, results_graph), cast(str, results_text)


def shacl_validation_to_markdown(results_graph: Graph) -> str:
    """
    Converts a SHACL validation report graph into a human-readable Markdown report.
    """
    SH = Namespace("http://www.w3.org/ns/shacl#")
    CDI = Namespace("http://ddialliance.org/Specification/DDI-CDI/1.0/RDF/")
    SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

    prefixes = {
        str(CDI): "cdi:",
        str(SKOS): "skos:",
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf:",
        "http://www.w3.org/2000/01/rdf-schema#": "rdfs:",
        "http://www.w3.org/ns/shacl#": "sh:",
        "http://www.w3.org/2001/XMLSchema#": "xsd:",
    }

    def shorten(uri: Any) -> str:
        if not uri:
            return ""
        s = str(uri)
        for p, sub in prefixes.items():
            if s.startswith(p):
                return s.replace(p, sub)
        if "#" in s:
            return s.split("#")[-1]
        return s

    constraint_labels = {
        str(SH.ClosedConstraintComponent): "Unexpected property (not allowed by model)",
        str(SH.MinCountConstraintComponent): "Missing required property",
        str(SH.MaxCountConstraintComponent): "Too many values for property",
        str(SH.DatatypeConstraintComponent): "Invalid data type",
        str(SH.NodeConstraintComponent): "Value does not match expected structure/type",
        str(SH.ClassConstraintComponent): "Value must be an instance of a specific class",
        str(SH.PatternConstraintComponent): "Value does not match required format (regex)",
        str(SH.InConstraintComponent): "Value is not in the allowed list",
    }

    report = results_graph.value(predicate=RDF.type, object=SH.ValidationReport)
    conforms = results_graph.value(report, SH.conforms)

    md = []
    md.append("# DDI-CDI Validation Report\n")

    status = "✅ PASS" if conforms else "❌ FAIL"
    md.append(f"**Status:** {status}\n")

    results = list(results_graph.subjects(RDF.type, SH.ValidationResult))

    if not results:
        if conforms:
            md.append("No violations found. The graph is perfectly valid according to DDI-CDI 1.0.0 SHACL rules.")
        else:
            md.append("The graph does not conform, but no specific validation results were found in the report.")
        return "\n".join(md)

    nodes: dict[str, list[Any]] = {}
    for res in results:
        focus_node = results_graph.value(res, SH.focusNode)
        node_str = str(focus_node)
        if node_str not in nodes:
            nodes[node_str] = []
        nodes[node_str].append(res)

    md.append("## Summary\n")
    md.append(f"- **Total Issues Found**: {len(results)}")
    md.append(f"- **Affected Objects**: {len(nodes)}")
    md.append("")

    md.append("## Issues by Object\n")

    for node_uri in sorted(nodes.keys()):
        node_results = nodes[node_uri]
        md.append(f"### Object: `{shorten(node_uri)}`")

        for res in node_results:
            severity = results_graph.value(res, SH.resultSeverity)
            severity_label = (
                "Violation" if severity == SH.Violation else "Warning" if severity == SH.Warning else "Info"
            )
            message = results_graph.value(res, SH.resultMessage)
            path = results_graph.value(res, SH.resultPath)
            component = results_graph.value(res, SH.sourceConstraintComponent)
            value = results_graph.value(res, SH.value)

            icon = "🔴" if severity == SH.Violation else "🟠" if severity == SH.Warning else "🔵"

            md.append(f"#### {icon} {severity_label}: {constraint_labels.get(str(component), shorten(component))}")

            if message and "Value does not conform to Shape" not in str(message):
                md.append(f"**Description:** {message}")

            if path:
                md.append(f"- **Property:** `{shorten(path)}`")

            if value:
                md.append(f"- **Problematic Value:** `{shorten(value)}`")

            md.append("")

        md.append("---")

    return "\n".join(md)
