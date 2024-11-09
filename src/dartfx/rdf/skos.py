from typing import Optional
from dartfx.rdf import rdf

from dataclasses import dataclass, field
from rdflib import SKOS

@dataclass(kw_only=True)
class SkosResource(rdf.RdfResource):
    def __post_init__(self):
        if hasattr(super(), '__post_init__'):
            super().__post_init__()
        self._namespace = SKOS

@dataclass(kw_only=True)
class SkosClass(SkosResource):
    prefLabel: Optional[list["PrefLabel"]] = field(default_factory=list)
    altLabel: Optional[list["AltLabel"]] = field(default_factory=list)
    hiddenLabel: Optional[list["HiddenLabel"]] = field(default_factory=list)
    
    notation: Optional[list["Notation"]] = field(default_factory=list)
    note: Optional[list["Note"]] = field(default_factory=list)
    changeNote: Optional[list["ChangeNote"]] = field(default_factory=list)
    definition: Optional[list["Definition"]] = field(default_factory=list)
    editorialNote: Optional[list["EditorialNote"]] = field(default_factory=list)
    example: Optional[list["Example"]] = field(default_factory=list)
    historyNote: Optional[list["HistoryNote"]] = field(default_factory=list)
    scopeNote: Optional[list["ScopeNote"]] = field(default_factory=list)
    
    def add_pref_label(self, label: str, lang: Optional[str] = None):
        self.prefLabel.append(PrefLabel(value=label, lang=lang))
        
    def add_alt_label(self, label: str, lang: Optional[str] = None):
        self.altLabel.append(AltLabel(value=label, lang=lang))

    def add_hidden_label(self, label: str, lang: Optional[str] = None):
        self.hiddenLabel.append(HiddenLabel(value=label, lang=lang))
        
    def add_notation(self, label: str, lang: Optional[str] = None):
        self.notation.append(Notation(value=label, lang=lang))
        
    def add_note(self, label: str, lang: Optional[str] = None):
        self.note.append(Note(value=label, lang=lang))
        
    def add_change_note(self, label: str, lang: Optional[str] = None):
        self.changeNote.append(ChangeNote(value=label, lang=lang))
        
    def add_definition(self, label: str, lang: Optional[str] = None):
        self.definition.append(Definition(value=label, lang=lang))
        
    def add_editorial_note(self, label: str, lang: Optional[str] = None):
        self.editorialNote.append(EditorialNote(value=label, lang=lang))
        
    def add_example(self, label: str, lang: Optional[str] = None):
        self.example.append(Example(value=label, lang=lang))
        
    def add_history_note(self, label: str, lang: Optional[str] = None):
        self.historyNote.append(HistoryNote(value=label, lang=lang))
        
    def add_scope_note(self, label: str, lang: Optional[str] = None):
        self.scopeNote.append(ScopeNote(value=label, lang=lang))
    
@dataclass(kw_only=True)
class SkosProperty(SkosResource):
    pass

#
# CLASSES
#
@dataclass(kw_only=True)
class ConceptScheme(SkosClass):
    inScheme: Optional[list["ConceptScheme"]] = field(default_factory=list)
    hasTopConcept: Optional[list["Concept"]] = field(default_factory=list)
    
    def add_in_scheme(self, scheme: "ConceptScheme"):
        self.inScheme.append(scheme)
        
    def add_has_top_concept(self, concept: "Concept"):
        self.hasTopConcept.append(concept)
        
@dataclass(kw_only=True)    
class Concept(SkosClass):
    related: Optional[list["Concept"]] = field(default_factory=list)
    broaderTransitive: Optional[list["Concept"]] = field(default_factory=list)
    broader: Optional[list["Concept"]] = field(default_factory=list)
    narrowerTransitive: Optional[list["Concept"]] = field(default_factory=list)
    narrower: Optional[list["Concept"]] = field(default_factory=list)
    
    closeMatch: Optional[list["Concept"]] = field(default_factory=list)
    exactMatch: Optional[list["Concept"]] = field(default_factory=list)
    relatedMatch: Optional[list["Concept"]] = field(default_factory=list)   
    broaderMatch: Optional[list["Concept"]] = field(default_factory=list)

    topConceptOf: Optional[list["Concept"]] = field(default_factory=list)

    def add_related(self, concept: "Concept"):
        self.related.append(concept)
        
    def add_broader_transitive(self, concept: "Concept"):
        self.broaderTransitive.append(concept)
        
    def add_broader(self, concept: "Concept"):
        self.broader.append(concept)
        
    def add_narrower_transitive(self, concept: "Concept"):
        self.narrowerTransitive.append(concept)
        
    def add_narrower(self, concept: "Concept"):
        self.narrower.append(concept)
        
    def add_close_match(self, concept: "Concept"):
        self.closeMatch.append(concept)
        
    def add_exact_match(self, concept: "Concept"):
        self.exactMatch.append(concept)
        
    def add_related_match(self, concept: "Concept"):
        self.relatedMatch.append(concept)
        
    def add_broader_match(self, concept: "Concept"):
        self.broaderMatch.append(concept)

    def add_top_concept_of(self, scheme: "ConceptScheme"):
        self.topConceptOf.append(scheme)
   

#
#  Lexical Labels Properties 
#

@dataclass(kw_only=True)
class PrefLabel(SkosProperty, rdf.RdfString):
    pass

@dataclass(kw_only=True)
class AltLabel(SkosProperty, rdf.RdfString):
    pass

@dataclass(kw_only=True)
class HiddenLabel(SkosProperty, rdf.RdfString):
    pass


#
#  Notation Properties 
#
@dataclass(kw_only=True)
class Notation(SkosProperty, rdf.RdfString):
    pass

#
#  Documentation Properties 
#
@dataclass(kw_only=True)
class Note(SkosProperty, rdf.RdfString):
    pass

@dataclass(kw_only=True)
class ChangeNote(Note):
    pass

@dataclass(kw_only=True)
class Definition(Note):
    pass

@dataclass(kw_only=True)
class Example(Note):
    pass

@dataclass(kw_only=True)
class EditorialNote(Note):
    pass

@dataclass(kw_only=True)
class HistoryNote(Note):
    pass

@dataclass(kw_only=True)
class ScopeNote(Note):
    pass

#
#  Semantic Relations Properties 
#
@dataclass(kw_only=True)
class SemanticRelation(SkosProperty, rdf.Uri):
    pass

@dataclass(kw_only=True)
class BroaderTransitive(SemanticRelation):
    pass

@dataclass(kw_only=True)
class Broader(BroaderTransitive):
    pass

@dataclass(kw_only=True)
class NarrowerTransitive(SemanticRelation): 
    pass

@dataclass(kw_only=True)
class Narrower(NarrowerTransitive):
    pass

@dataclass(kw_only=True)
class Related(SemanticRelation):
    pass


#
#  Mapping Properties 
#
@dataclass(kw_only=True)
class MappingRelation(SemanticRelation):
    pass

@dataclass(kw_only=True)
class CloseMatch(MappingRelation):
    pass

@dataclass(kw_only=True)
class ExactMatch(CloseMatch):
    pass

@dataclass(kw_only=True)
class RelatedMatch(MappingRelation):
    pass

@dataclass(kw_only=True)
class BroaderMatch(MappingRelation):
    pass

@dataclass(kw_only=True)
class NarrowMatch(MappingRelation):
    pass

