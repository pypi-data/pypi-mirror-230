from typing import List, Any, Dict, Optional, Union
from pydantic import BaseModel, validator, Field
from enum import Enum
from xcloud.utils.logging import configure_logger
from xcloud.config import Config
from pathlib import Path
from urllib.parse import urlparse
import json


logger = configure_logger(__name__)


class Cloud(str, Enum):
    AWS = "aws"
    GCP = "gcp"
    
    
class GCPRegion(str, Enum):
    US_CENTRAL_1 = "us-central1"


class Location(BaseModel):
    cloud: Optional[Cloud] = Cloud.GCP
    # It will be a union of GCPRegion, AWSRegion, AzureRegion, etc
    region: Optional[GCPRegion] = GCPRegion.US_CENTRAL_1
    
    class Config:
        validate_all = True
        
    @validator("region")
    def validate_region(cls, v, values: Dict[str, Any]):
        if values["cloud"] == Cloud.GCP and not isinstance(v, GCPRegion):
            assert False, "The region selected does not match with the cloud"
            
        return v
            

class Metadata(BaseModel):
    error: Optional[str]
    ended_at: Optional[int]
    started_at: Optional[int]
    started_reason: Optional[str]
    cancelled_at: Optional[str]
    cancelled_reason: Optional[str]
    deleted_at: Optional[str]
    deleted_reason: Optional[str]
    
    class Config:
        validate_all = True

class MachineType(str, Enum):
    CPU_SMALL = "cpu_small"
    CPU_MEDIUM = "cpu_medium"
    CPU_LARGE = "cpu_large"
    CPU_XLARGE = "cpu_xlarge"
    GPU_T4_1 = "gpu_t4_1"
    GPU_T4_2 = "gpu_t4_2"
    GPU_T4_4 = "gpu_t4_4"
    GPU_L4_1 = "gpu_l4_1"
    GPU_L4_2 = "gpu_l4_2"
    GPU_L4_4 = "gpu_l4_4"
    GPU_L4_8 = "gpu_l4_8"
    GPU_V100_1 = "gpu_v100_1"
    GPU_V100_2 = "gpu_v100_2"
    GPU_V100_4 = "gpu_v100_4"
    GPU_V100_8 = "gpu_v100_8"
    GPU_A100_40_SEVENTH = "gpu_a100_40_seventh"
    GPU_A100_40_HALF = "gpu_a100_40_half"
    GPU_A100_40_1 = "gpu_a100_40_1"
    GPU_A100_40_2 = "gpu_a100_40_2"
    GPU_A100_40_4 = "gpu_a100_40_4"
    GPU_A100_40_8 = "gpu_a100_40_8"
    GPU_A100_40_16 = "gpu_a100_40_16"
    GPU_A100_80_SEVENTH = "gpu_a100_80_seventh"
    GPU_A100_80_HALF = "gpu_a100_80_half"
    GPU_A100_80_1 = "gpu_a100_80_1"
    GPU_A100_80_2 = "gpu_a100_80_2"
    GPU_A100_80_4 = "gpu_a100_80_4"
    GPU_A100_80_8 = "gpu_a100_80_8"   

class Status(str, Enum):
    SUCCESSFUL = "successful"
    FAILED = "failed"
    RUNNING = "running"
    NOT_STARTED = "not_started"
    CANCELLED = "cancelled"
    CANCELLING = "cancelling"
    DEPLOYING = "deploying"
    
class Credentials(BaseModel):
    aws_access_key_id: Optional[str] = Field(repr=False)
    aws_secret_access_key: Optional[str] = Field(repr=False)
    aws_region: Optional[str] = Field(repr=False)
    application_credentials: Optional[Union[str, Dict]] = Field(repr=False)
    cloud: Cloud
    
    @validator("aws_access_key_id")
    def validate_aws_access_key_id(cls, v):
        return v
    
    @validator("aws_secret_access_key")
    def validate_aws_secret_access_key(cls, v):
        return v
    
    @validator("aws_region")
    def validate_aws_region(cls, v):
        return v
    
    @validator("application_credentials")
    def validate_application_credentials(cls, v):
        if v is not None and isinstance(v, str):
            application_credentials_path = Path(v)
            assert application_credentials_path.is_file(), "application_credentials should be a path to a file"
            
            with open(str(application_credentials_path.resolve())) as f:
                application_credentials_content = json.loads(f.read())
        
            return application_credentials_content
        return v
    
    @validator("cloud")
    def validate_cloud(cls, v, values, **kwargs):
        valid_clouds = [Cloud.AWS, Cloud.GCP, None]
        
        assert v in valid_clouds, f"Valid clouds are {valid_clouds}"
        
        if v == Cloud.AWS:
            condition = "aws_access_key_id" in values and "aws_secret_access_key" in values and "aws_region" in values
            
            if not condition:
                logger.warning("AWS credentials have not been provided")
                
        if v == Cloud.GCP:
            condition = "application_credentials" in values
            
            if not condition:
                logger.warning("Google application_credentials have not been provided")
        
        return v
    
    class Config:
        validate_all = True 
