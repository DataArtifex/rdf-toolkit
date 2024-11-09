from rdflib import Graph
from dartfx.rdf import skos

def to_graph(resources: list[skos.SkosResource]):
    g = Graph()
    for resource in resources:
        resource.add_to_rdf_graph(g)
    return g

def test_skos_yesno():
    resources = []
    scheme = skos.ConceptScheme()
    resources.append(scheme)
    
    yes = skos.Concept()
    yes.add_notation("Y")
    yes.add_pref_label("yes")
    resources.append(yes)
    scheme.add_has_top_concept(yes)
    
    no = skos.Concept()
    no.add_notation("N")
    no.add_pref_label("no")
    resources.append(no)
    scheme.add_has_top_concept(no)
    
    g = to_graph(resources)
    print(g.serialize(format="turtle"))
