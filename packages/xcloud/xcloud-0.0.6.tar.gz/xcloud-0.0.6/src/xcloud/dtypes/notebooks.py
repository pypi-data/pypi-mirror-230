from typing import Dict, Optional
from pydantic import BaseModel, Field, validator
from fastapi import HTTPException
import re 
from xcloud.dtypes.shared import MachineType, Metadata, Status
from xcloud.dtypes.shared import Location


class NotebookContainerSpecs(BaseModel):
    machine_type: MachineType = MachineType.GPU_T4_1
    spot: Optional[bool] = True
    image: Optional[str]
    env: Optional[Dict[str, str]]
    secrets: Optional[Dict[str, str]] = Field(repr=False)

    class Config:
        validate_all = True
        
        
class NotebookAccessDetails(BaseModel):
    base_url: Optional[str]
    token: Optional[str]
    full_url: Optional[str]
   
        
class Notebook(BaseModel):
    notebook_name: str
    workspace_id: Optional[str]
    status: Status = Status.NOT_STARTED
    container_specs: NotebookContainerSpecs
    location: Optional[Location] = Field(default_factory=Location)
    access_details: Optional[NotebookAccessDetails] = Field(default_factory=NotebookAccessDetails)
    on_premise: Optional[bool] = False
    link_name: Optional[str] = None
    metadata: Optional[Metadata] = Field(default_factory=Metadata)
    
    class Config:
        validate_all = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        
    @validator("metadata")
    def validate_metadata(cls, v):
        if v is None:
            return Metadata()
        
        return v
        
    @validator("notebook_name")
    def validate_notebook_name(cls, v):
        regex = "^[a-z0-9]([-a-z0-9]*[a-z0-9])?([a-z0-9]([-a-z0-9]*[a-z0-9])?)*$"
        
        if len(v) > 30:
            raise HTTPException(
                status_code=422,
                detail="The notebook name cannot be longuer than 30 characters. Currently {}".format(len(v))
            )
        
        if not bool(re.match(regex, v)):
            raise HTTPException(
                status_code=422,
                detail="The notebook_name must consist of lower case alphanumeric characters. Regex used for validation is '^[a-z0-9]([-a-z0-9]*[a-z0-9])?([a-z0-9]([-a-z0-9]*[a-z0-9])?)*$'"
            )
        
        return v   
