
from abc import ABC, abstractmethod
import uuid
from .rdf import Uri


#
# URI Generators
#

class UriGenerator(ABC):
    
    @abstractmethod
    def get_string(self, *args, **kwargs) -> str:
        pass    
    
    @abstractmethod
    def get_uri(self, *args, **kwargs) -> Uri:
        pass
    
class UuidUrnGenerator():
    
    def get_string(self, *args, **kwargs) -> str:
        return uuid.uuid4().urn
    
    def get_uri(self, *args, **kwargs) -> Uri:
        return Uri(value=self.get_string())
        
class UrlUriGenerator(UriGenerator):
    base_url: str
    
    def __init__(self, base_url: str = "http://example.org"):
        self.base_url = base_url
        
    def get_string(self, ids: str|list[str], *args, **kwargs) -> str:
        if isinstance(ids, str):
            return f"{self.base_url}/{ids}"
        else:
            return [f"{self.base_url}/{i}" for i in ids]        

class UrnUriGenerator(UriGenerator):
    base_urn: str
    
    def __init__(self, base_urn: str = "urn:foo"):
        self.base_url = base_urn
    