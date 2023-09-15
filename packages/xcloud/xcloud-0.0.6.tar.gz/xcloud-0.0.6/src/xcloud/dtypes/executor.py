from typing import Dict, List, Optional, Union
from pydantic import BaseModel, validator, Field
import re
from xcloud.dtypes.shared import Status, Credentials, MachineType, Metadata
from xcloud.dtypes.shared import Location
        
class CodeSpecs(BaseModel):
    credentials: Optional[Credentials]
    code_dir: Optional[str]
    
class ExecutionContainerSpecs(BaseModel):
    machine_type: MachineType = MachineType.GPU_T4_1
    spot: Optional[bool] = True
    image: str
    command: Optional[List[str]]
    args: Optional[List[str]]
    env: Optional[Dict[str, str]]
    secrets: Optional[Dict[str, str]] = Field(repr=False)
    
class ExecutionJob(BaseModel):
    job_name: str
    workspace_id: Optional[str]
    status: Status = Status.NOT_STARTED
    container_specs: List[ExecutionContainerSpecs]
    location: Optional[Location] = Field(default_factory=Location)
    code_specs: Optional[CodeSpecs]
    on_premise: Optional[bool] = False
    link_name: Optional[str] = None
    metadata: Optional[Metadata]
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        validate_all = True 
        
    @validator("job_name")
    def validate_job_name(cls, v):
        regex = "^[a-z0-9]([-a-z0-9]*[a-z0-9])?([a-z0-9]([-a-z0-9]*[a-z0-9])?)*$"
        
        assert len(v) <= 30, "The job name cannot be longuer than 30 characters. Currently {}".format(len(v))
        
        assert bool(re.match(regex, v)), "The job_name must consist of lower case alphanumeric characters. Regex used for validation is '^[a-z0-9]([-a-z0-9]*[a-z0-9])?([a-z0-9]([-a-z0-9]*[a-z0-9])?)*$'"
        
        return v
