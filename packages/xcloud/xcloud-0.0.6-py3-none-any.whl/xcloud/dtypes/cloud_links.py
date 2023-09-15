from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, validator
from xcloud.dtypes.shared import Metadata

    
class Protocol(str, Enum):
    HTTPS = "https"
    HTTP = "http"    

    
class Endpoints(BaseModel):
    ingress_ip_or_domain: str
    notebooks_ip_or_domain: str
    inference_ip_or_domain: str
    protocol: Optional[Protocol] = Protocol.HTTPS
        
    class Config:
        validate_all = True


class Link(BaseModel):
    link_name: str
    workspace_id: Optional[str]
    on_premise_license: Optional[str]
    endpoints: Endpoints
    metadata: Optional[Metadata]
    
    class Config:
        validate_all = True
