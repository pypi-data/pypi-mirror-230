from typing import List, Any, Dict, Optional
from pydantic import BaseModel, Field, validator, root_validator
import re
from enum import Enum
from xcloud.dtypes.shared import Status, Credentials, MachineType, Metadata
from xcloud.config import Config
from xcloud.utils.pydantic_to_dict import map_pydantic_class_to_dict
from xcloud.dtypes.shared import Location
    
   
class ModelSpecs(BaseModel):
    model_path: Optional[str]
    credentials: Optional[Credentials]

class Batcher(BaseModel):
    max_batch_size: Optional[int] = 1
    # Max latency in milliseconds
    max_lantecy: Optional[int] = 1
    # batch request timeout in milliseconds
    # 20 secs by default
    timeout: Optional[int] = 240000

class SCALE_METRIC(str, Enum):
    CONCURRENCY = "concurrency"
    RPS = "rps"

class Scaling(BaseModel):
    time_before_scaling_to_zero: Optional[int] = 1800000
    min_replicas: Optional[int] = 1
    max_replicas: Optional[int] = 1
    scale_metric: Optional[SCALE_METRIC] = SCALE_METRIC.CONCURRENCY
    target_scaling_value: Optional[int] = 1
    
    @validator("min_replicas")
    def validate_min_replicas(cls, v):
        assert v >= 0, "min_replicas value of the scaling config cannot be lower than 0"
            
        return v
    
    @validator("max_replicas")
    def validate_max_replicas(cls, v, values):
        assert v >= 0, "max_replicas value of the scaling config cannot be lower than 0"
        
        assert v >= values['min_replicas'], "max_replicas value of the scaling config cannot be lower than the min_replicas value"
            
        return v
    
    @validator("scale_metric")
    def validate_scale_metric(cls, v):
        valid_scale_metrics = [SCALE_METRIC.CONCURRENCY, SCALE_METRIC.RPS]
        
        assert v in valid_scale_metrics, "The allowed scale_metrics are SCALE_METRIC.CONCURRENCY, SCALE_METRIC.RPS"
        
        return v
    
    @validator("target_scaling_value")
    def validate_target_scaling_value(cls, v):
        assert v >= 0, "target_scaling_value value of the scaling config cannot be lower than 0"

        return v
    
    class Config:
        validate_all = True 

    
class DeploymentSpecs(BaseModel):
    batcher: Optional[Batcher] = Field(default_factory=Batcher)
    scaling: Optional[Scaling] = Field(default_factory=Scaling)
    authentication: Optional[bool] = False
    
    
class Inference(BaseModel):
    base_endpoint: Optional[str]
    is_ready_endpoint: Optional[str]
    infer_endpoint: Optional[str]
    api_key: Optional[str]
    host: Optional[str]
    

class ModelType(str, Enum):
    T5 = "T5"
    BLOOM = "BLOOM"
    GPT2 = "GPT2"
    GPTJ = "GPTJ"
    GPT_NEO_X = "GPT_NEO_X"
    OPT = "OPT"
    LLAMA = "LLAMA"
    MPT = "MPT"
    
    
class GenerationParams(BaseModel):
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    top_k: Optional[int] = -1
    beam_search: Optional[bool] = False
    max_tokens: Optional[int] = 2048
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    
    
class DTYPES(str, Enum):
    FP16 = "fp16"
    BF16 = "bf16"
    FP32 = "fp32"


class ModelConfig(BaseModel):
    model_path: str
    tokenizer_path: str
    optimized_inference: Optional[bool] = True
    optimization_fallback: Optional[bool] = True
    dtype: Optional[DTYPES] = DTYPES.FP16
    tensor_parallel_size: Optional[int] = 1
    max_batch_size: Optional[int] = 8
    max_tokens: Optional[int] = 8192
    generation_params: Optional[GenerationParams] = Field(default_factory=GenerationParams)
    
    
class DeploymentOptimizationSpecs(BaseModel):
    model_type: ModelType
    model_config: ModelConfig


class DeploymentContainerSpecs(BaseModel):
    machine_type: MachineType = MachineType.GPU_T4_1
    spot: Optional[bool] = True
    image: Optional[str]
    command: Optional[List[str]]
    args: Optional[List[str]]
    env: Optional[Dict[str, str]]
    secrets: Optional[Dict[str, str]] = Field(repr=False)
    optimization_specs: Optional[DeploymentOptimizationSpecs]
    
    class Config:
        validate_all = True 
    
    @validator("optimization_specs")
    def validate_optimization_specs(cls, v: DeploymentOptimizationSpecs, values: Dict[str, Any]):
        if v is not None:
            if v.model_type == ModelType.T5:
                # Specify Docker image and ENV variables
                values["image"] = Config.DEFAULT_FT_DOCKER_IMAGE
            else:
                values["image"] = Config.DEFAULT_VLLM_DOCKER_IMAGE
                
            env_vars_dict = map_pydantic_class_to_dict(v.model_config)
            # Env vars added by the user
            prev_env = values["env"] if values["env"] is not None else {}
            values["env"] = {**prev_env, **env_vars_dict}
            # ENV var to force using the templating / optimizations engine
            # If this is not specified, it will go for the inference.py file
            values["env"]["MODEL_CONFIG_TEMPLATE_DEPLOYMENT"] = True
            
        return v
    

class Deployment(BaseModel):
    deployment_name: str
    workspace_id: Optional[str]
    status: Status = Status.NOT_STARTED
    model_specs: Optional[ModelSpecs]
    deployment_specs: Optional[DeploymentSpecs] = Field(default_factory=DeploymentSpecs)
    container_specs: DeploymentContainerSpecs
    location: Optional[Location] = Field(default_factory=Location)
    inference: Optional[Inference]
    on_premise: Optional[bool] = False
    link_name: Optional[str] = None
    metadata: Optional[Metadata]
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        validate_all = True 
        
    @validator("deployment_name")
    def validate_deployment_name(cls, v):
        regex = "^[a-z0-9]([-a-z0-9]*[a-z0-9])?([a-z0-9]([-a-z0-9]*[a-z0-9])?)*$"
        
        assert len(v) <= 30, "The deployment name cannot be longuer than 30 characters. Currently {}".format(len(v))
        
        assert bool(re.match(regex, v)), "The deployment_name must consist of lower case alphanumeric characters. Regex used for validation is '^[a-z0-9]([-a-z0-9]*[a-z0-9])?([a-z0-9]([-a-z0-9]*[a-z0-9])?)*$'"
        
        return v   
