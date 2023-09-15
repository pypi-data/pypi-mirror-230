from pydantic import BaseModel, Field, validator
from enum import Enum
from typing import Optional
from pathlib import Path
from xcloud.dtypes.shared import Metadata, Credentials
from xcloud.dtypes.deployments import Inference, DeploymentSpecs


class ModelsAPIModelFamily(str, Enum):
    LLAMA_V2_7B = "llama_v2_7b"
    LLAMA_V2_13B = "llama_v2_13b"
    LLAMA_V2_7B_CHAT = "llama_v2_7b_chat"
    LLAMA_V2_13B_CHAT = "llama_v2_13b_chat"


class ModelsAPIFinetuningType(str, Enum):
    UNSUPERVISED_FINETUNING = "unsupervised_finetuning"
    INSTRUCTION_FINETUNING = "instruction_finetuning"


class ModelsAPIFinetuning(BaseModel):
    workspace_id: Optional[str]
    finetuning_name: str
    model_name: str
    model_family: Optional[ModelsAPIModelFamily]
    num_epochs: Optional[int] = 3
    dataset_id: Optional[str]
    finetuning_type: ModelsAPIFinetuningType
    status: Optional[str]
    metadata: Optional[Metadata] = Field(default_factory=Metadata)
    
    class Config:
        validate_all = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        
    # @validator("dataset_path")
    # def validate_dataset_path(cls, v):
    #     if v is None:
    #         assert Path(v).is_file(), f"{v} is not a file. Please make sure it is a file"
    #         assert is_jsonl_file_valid(v), f"This JSONL file {v} is not valid"
        
    #     return v
    

class ModelsAPIDeployment(BaseModel):
    workspace_id: Optional[str]
    deployment_name: str
    model_name: str
    deployment_specs: Optional[DeploymentSpecs] = Field(default_factory=DeploymentSpecs)
    inference: Optional[Inference]
    status: Optional[str]
    metadata: Optional[Metadata] = Field(default_factory=Metadata)

    
class ModelsAPIModelType(str, Enum):
    BASE_MODEL = "base_model"
    FINETUNED_MODEL = "finetuned_model"
    
    
class ModelsAPIModelStatus(str, Enum):
    READY = "ready"
    NOT_READY = "not_ready"
    

class ModelsAPIModel(BaseModel):
    workspace_id: Optional[str]
    model_name: str
    model_type: ModelsAPIModelType
    model_family: ModelsAPIModelFamily
    status: ModelsAPIModelStatus
    deleted: bool = False
    metadata: Optional[Metadata] = Field(default_factory=Metadata)


class OnPremiseModelsAPIFinetuning(BaseModel):
    workspace_id: Optional[str]
    finetuning_name: str
    dataset_cloud_path: str
    saving_finetuning_code_cloud_path: str
    saving_model_cloud_path: str
    model_family: Optional[ModelsAPIModelFamily]
    num_epochs: Optional[int] = 3
    finetuning_type: ModelsAPIFinetuningType
    credentials: Credentials
    link_name: str
    status: Optional[str]
    metadata: Optional[Metadata] = Field(default_factory=Metadata)
    
    class Config:
        validate_all = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        

class OnPremiseModelsAPIDeployment(BaseModel):
    workspace_id: Optional[str]
    deployment_name: str
    model_cloud_path: Optional[str]
    model_family: ModelsAPIModelFamily
    deployment_specs: Optional[DeploymentSpecs] = Field(default_factory=DeploymentSpecs)
    inference: Optional[Inference]
    credentials: Credentials
    link_name: str
    status: Optional[str]
    metadata: Optional[Metadata] = Field(default_factory=Metadata)
