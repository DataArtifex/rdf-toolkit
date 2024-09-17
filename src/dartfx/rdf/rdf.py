from dataclasses import dataclass, field, fields
from datetime import date, datetime
from enum import Enum, auto
from functools import cache
import logging
import re
from typing import Any, Collection, Optional, Union, get_args, get_origin, get_type_hints
from urllib.parse import urlparse
import uuid
from rdflib import RDF, XSD, Graph, Literal, URIRef
import sys

@dataclass
class AttributeInfo:
    """
    Helper class to capture the information on an attribute.
    """
    name: str
    is_list: bool = None
    is_optional: bool = None
    cls: Any = None # the attribute or list class
    metadata: Any = None # metadata from the field(...,metadata="")
    
    @property
    def associated_class(self):
        if self.metadata:
            return self.metadata.get("association")    

@dataclass(kw_only=True)
class RdfResource:
    # work in progress (ignore for now)
    #_extended_attributes: Optional[Graph] = field(default=None)
    _uri: str = field(default=None, init=False)
    _namespace: str = field(default=None, init=False)

    def __init__(self):
        self.g = Graph()

    @classmethod
    @cache
    def _get_attribute_info(cls, attribute_name:str) -> AttributeInfo:
        """Internal helper that infers information on an attribute type for instantiaion and processing.

        Relies on dataclasses attribute annotations and Python typing package introspection.
        
        Note that we use the attribute field(...) 'metadata' to capture information specific to the DDI-CDI model

        """
        #
        # A typical attribute is defined as 
        #   name: Optional[list["ObjectName"]] = field(... )
        # which translates into
        #   name_type_hints is typing.Optional[list['ObjectName']]
        #   --> origin is typing.Union
        #   --> args is the tuple (typinglist['ObjectName'], <class 'NoneType'>)
        #
        attribute_info= AttributeInfo(name=attribute_name)
        # Field information
        try:
            field_info = next(f for f in fields(cls) if f.name == attribute_name)
        except StopIteration:
            raise Exception(f"{attribute_name} attribute not found on {cls.__name__}")
        attribute_info.metadata = field_info.metadata
        # Type hints
        attribute_type_hints = get_type_hints(cls).get(attribute_name)
        if attribute_type_hints:
            origin = get_origin(attribute_type_hints)
            args = list(get_args(attribute_type_hints)) # we make the args tuple a list so we can remove the None class
            if origin is Union: 
                if None.__class__ in args:
                    attribute_info.is_optional = True
                    args.remove(None.__class__) # remove the None class
                else:
                    attribute_info.is_optional = False
                # At this point, only one type should be left
                # It could be a list
                if len(args) == 1:
                    attribute_type_hints = args[0]
                    origin = get_origin(attribute_type_hints)
                    args = list(get_args(attribute_type_hints))
                else:
                    # More than one type is possible
                    # ... but we do not currently support this
                    raise Exception(f"More than one type found for {attribute_type_hints}")
        else:
            # This attributes does not exists on the class
            # Just ignore and return None
            logging.warning(f"No '{attribute_name}' attribute found on {cls.__name__}")
            return None
        # detect if this is a list or a single value
        attribute_info.is_list = True if origin is list else False
        if attribute_info.is_list:
            attribute_info.cls = args[0]
        else:
            attribute_info.cls = attribute_type_hints
        # If the type was defined using a ForwardRef, 
        # convert the string value to a class 
        if isinstance(attribute_info.cls, str):
            local_class = locals()['cls'] # this return the class holding the attribute
            module_name = local_class.__module__ # this is the name of the wrapping class module (e.g. dartfx.dcat.dcat)
            # Get the class from sys.modules
            # https://stackoverflow.com/questions/1176136/convert-string-to-python-class-object
            attribute_info.cls = getattr(sys.modules[module_name], attribute_info.cls)
        # Done
        return attribute_info

    #
    # private attributes getters/setters
    #
    def get_namespace(self) -> str:
        return self._namespace

    def get_uri(self) -> str:
        # if URI is not set, generate a random uuid based URI
        if self._uri is None:
            self._uri = uuid.uuid4().urn
        return self._uri

    def get_uriref(self) -> URIRef:
        return URIRef(self.get_uri())

    def set_uri(self, uri: str):
        self._uri = uri
        
    def set_namespace(self, namespace: str):
        self.namespace = namespace

    def add_to_rdf_graph(self, g:Graph, use_list=False) -> URIRef:
        """ 
        Add this resource to an RDF graph.
        
        A nifty method that turn this resource into a stack of RDF triples and adds them to the specified RDF graph.
        
        It makes the following assumptions:
        - The resource is a dataclass
        - The dataclass properties are the class attribute name
        - Attributes starting with an underscore are ignored
        - The attribute namespace is the same as the resource, unless overridden in the attribute metadata
        
        """
        # check namespace
        if not self._namespace:
            raise Exception(f"Resource {self.__class__.__name__} has no namespace")
        else:
            namespace = self._namespace
        # create the resource subject
        subject = self.get_uriref()
        triple = (subject, RDF.type, namespace[self.__class__.__name__])
        # if resource already in the graph, just return the reference
        if triple in g:
            return subject
        #logging.debug(f"Adding {triple[0]} {triple[2]} to RDF graph") 
        g.add(triple)
        
        for attribute in fields(self): # iterate over all fields (attributes)
            # skip private attributes
            if attribute.name.startswith("_"):
                continue
            # process attribute
            attribute_value = getattr(self, attribute.name, None) 
            if attribute_value: # if the attribute is not None or en empty list
                # determine the attribute namesspace
                # by default, this is the same as the resource, but can be overridden by the attribute metadata
                if 'namespace' in attribute.metadata:
                    attribute_namespace = attribute.metadata["namespace"]
                else:
                    attribute_namespace = namespace
                # the RDF predicate is based on the attribute name and namespace
                predicate = attribute_namespace[attribute.name] # the RDF predicate is based on the attribute name
                # collecte information on this attribute
                attribute_info = self._get_attribute_info(attribute.name)
                # if not a list, convert to a single entry list so we can iterate
                if not attribute_info.is_list:
                    attribute_value_items = [attribute_value]
                else:
                    attribute_value_items = attribute_value
                # this array will collect all the objects that need to be added
                objects = [] 
                # iterate over all values and add
                for value in attribute_value_items:
                    if issubclass(attribute_info.cls, RdfResource):
                        object = value.add_to_rdf_graph(g)
                        objects.append(object)
                    elif issubclass(attribute_info.cls, str):
                        objects.append(Literal(value, datatype=XSD.string))
                    elif issubclass(attribute_info.cls, int):
                        objects.append(Literal(value, datatype=XSD.integer))
                    elif issubclass(attribute_info.cls, float):
                        objects.append(Literal(value, datatype=XSD.float))
                    elif issubclass(attribute_info.cls, bool):
                        objects.append(Literal(value, datatype=XSD.boolean))
                    elif issubclass(attribute_info.cls, datetime):
                        objects.append(Literal(value.isoformat(), datatype=XSD.dateTime))
                    elif issubclass(attribute_info.cls, date):
                        objects.append(Literal(value.isoformat(), datatype=XSD.date))
                    else:
                        objects.append(Literal(value))
                # add to this resource
                if attribute_info.is_list:
                    if use_list:
                        # Create a list node with a URIRef based on the subject and attribute
                        # Do not use blank node.
                        list_node = URIRef(f"{str(subject)}_{attribute.name}List")
                        rdf_list = Collection(g, list_node, objects)  # noqa: F841
                        g.add((subject, predicate, list_node)) # add the list_node, not rdf_list
                    else:
                        # add each entry as a triple
                        for object in objects:
                            g.add((subject, predicate, object))
                else:
                    # add single entry (there can only be one entry in this case)
                    g.add((subject, predicate, objects[0]))
        # return the URIRef                
        return subject

@dataclass(kw_only=True)
class RdfClass(RdfResource):
    pass

@dataclass(kw_only=True)
class RdfProperty(RdfResource):
    pass

class RdfStringDirection(Enum):
    LTR = auto()  # Left-to-Right
    RTL = auto()  # Right-to-Left

    def __str__(self):
        return self.name.lower()

    @classmethod
    def from_string(cls, direction_str):
        direction_str = direction_str.upper()
        if direction_str in cls.__members__:
            return cls[direction_str]
        else:
            raise ValueError(f"Invalid direction: {direction_str}")
   
@dataclass(kw_only=True)
class RdfLiteralDeprecated(RdfResource):
    value: any
    datatype: Optional["Uri"] = field(default=None)
    lang: Optional[str] = field(default=None)
    direction: Optional[RdfStringDirection] = field(default=None)
    
    def add_to_rdf_graph(self, g:Graph, use_list=False) -> URIRef:
        if isinstance(self.value, str):
            return Literal(self.value, datatype=XSD.string)
        elif isinstance(self.value, int):
            return Literal(self.value, datatype=XSD.int)
        elif isinstance(self.value, float):
            return Literal(self.value, datatype=XSD.float)
        elif isinstance(self.value, bool):
            return Literal(self.value, datatype=XSD.boolean)
        elif isinstance(self.value, datetime.datetime):
            return Literal(self.value, datatype=XSD.dateTime)
        elif isinstance(self.value, datetime.date):
            return Literal(self.value, datatype=XSD.date)
        else:
            raise ValueError(f"Unexpected literal type {type(self.value)}")
        
        
@dataclass(kw_only=True)
class RdfString(RdfResource):
    value: str
    lang: Optional[str] = field(default=None) # The language code
    direction: Optional[RdfStringDirection] = field(default=None)

    @staticmethod
    def validate_lang(lang: str) -> bool:
        if lang is not None and not re.match(r'^[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})*$', lang):
            return False
        else:
            return True

    def add_to_rdf_graph(self, g:Graph, use_list=False) -> URIRef:
        if self.value:
            if self.lang and not self.validate_lang(self.lang):
                raise ValueError(f"Invalid language code {self.lang}")
        # NOTE: direction is currently not supported by Literal
        return Literal(self.value, lang=self.lang, datatype=XSD.string)


@dataclass(kw_only=True)
class Uri(RdfProperty):
    value: str  # The URI value
    _valid_schemes: Optional[list[str]] = field(default_factory=lambda: ['http', 'https', 'ftp', 'urn'])

    def __post_init__(self):
        """Validate the URI after initialization."""
        self.validate_uri(self.value)

    def validate_uri(self,uri: str) -> bool:
        """Validate if the provided string is a well-formed URI."""
        parsed = urlparse(uri)
        # Check if the scheme is valid
        if parsed.scheme not in self.valid_schemes:
            raise ValueError(f"Invalid URI: {uri} -- invalid scheme {parsed.scheme}. Must be in {self.valid_schemes}") 
        # Additional checks based on the scheme
        if parsed.scheme in ['http', 'https', 'ftp']:
            # For HTTP, HTTPS, and FTP, check if the netloc (domain) is present
            if not parsed.netloc:
                raise ValueError(f"Invalid URI: {uri} -- invalid network location {parsed.netloc}")
        elif parsed.scheme == 'urn':
            # For URNs, validate the format
            urn_pattern = re.compile(r'^urn:[a-zA-Z0-9][a-zA-Z0-9-]{0,31}:[a-zA-Z0-9()+,\-.:=@;$_!*\'%/?#]+$')
            if not urn_pattern.match(uri):
                raise ValueError(f"Invalid URI: {uri} -- invalid pattern")
        # If all checks pass, the URI is valid
        return True
    
    @property
    def valid_schemes(self) -> list[str]:
        return self._valid_schemes

    @valid_schemes.setter
    def valid_schemes(self, valid_schemes: list[str]):
        self._valid_schemes = valid_schemes
    
    def is_valid_uri(self, uri: str, as_url=False, as_urn=False) -> bool:
        """Validate if the provided string is a well-formed URI."""
        try:
            self.validate_uri(uri)
            return True
        except ValueError:
            return False

    def to_string(self) -> str:
        """Return the URI as a string."""
        return self.value

    @classmethod
    def from_string(cls, uri_string: str) -> 'Uri':
        """Create an XsdAnyUri instance from a string."""
        return cls(value=uri_string)
    
    def add_to_rdf_graph(self, g: Graph) -> URIRef:
        """Override the add_to_rdf_graph method to simply return the URI as a URIRef.""" 
        return URIRef(self.value)

@dataclass(kw_only=True)
class Url(Uri):
    
    def __post_init__(self):
        self.valid_schemes = ['http', 'https']
        super().__post_init__()


@dataclass(kw_only=True)
class UriOrString(Uri):
    """A hybrid property type that can be either a URI or a string."""
    lang: Optional[str] = field(default=None)

    def __post_init__(self):
        pass # do not validate as URI
    
    def add_to_rdf_graph(self, g: Graph):
        if self.is_valid_uri(self.value):
            return URIRef(value=self.value)
        else:
            return Literal(self.value, lang=self.lang) #RDf Literal
