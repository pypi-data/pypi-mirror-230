from xcloud.utils.requests_utils import do_request
from xcloud.config import Config
from xcloud.dtypes.models_api import (
    ModelsAPIFinetuning, 
    ModelsAPIDeployment, 
    ModelsAPIModel,
    OnPremiseModelsAPIFinetuning,
    OnPremiseModelsAPIDeployment
)
from xcloud.utils.validations import is_jsonl_file_valid
from typing import List, Optional, Union
from pathlib import Path
import requests
import time


class ModelsAPIClient:
    @classmethod
    def get_finetunings(cls, workspace_id: Optional[str] = None) -> List[ModelsAPIFinetuning]:        
        response = do_request(
            url="{}/v1/finetunings/".format(
                Config.MODELS_API_BASE_URL_X_BACKEND
            ),
            http_method="get",
            workspace_id=workspace_id
        )
        
        list_finetunings_dicts = response.json()["data"]
        deployments = []
        
        for deployment_dict in list_finetunings_dicts:
            deployment = ModelsAPIFinetuning.parse_obj(deployment_dict)
            deployments.append(deployment)
            
        return deployments
    
    @classmethod
    def get_finetuning_by_name(cls, finetuning_name: str, workspace_id: Optional[str] = None) -> ModelsAPIFinetuning:        
        response = do_request(
            url="{}/v1/finetunings/{}".format(
                Config.MODELS_API_BASE_URL_X_BACKEND,
                finetuning_name
            ),
            http_method="get",
            workspace_id=workspace_id
        )
        
        finetuning_dict = response.json()["data"]
        finetuning = ModelsAPIFinetuning.parse_obj(finetuning_dict)
        
        return finetuning
    
    @classmethod
    def delete_finetuning(cls, finetuning_name: str, reason: str = "", workspace_id: Optional[str] = None) -> ModelsAPIFinetuning:
        response = do_request(
            url="{}/v1/finetunings/{}".format(
                Config.MODELS_API_BASE_URL_X_BACKEND,
                finetuning_name
            ),
            params={
                "hard_delete": True,
                "reason": reason
            },
            http_method="delete",
            workspace_id=workspace_id
        )
        
        finetuning_dict = response.json()["data"]
        finetuning = ModelsAPIFinetuning.parse_obj(finetuning_dict)
        return finetuning
    
    @classmethod
    def upload_dataset(cls, dataset_path: Union[str, Path], workspace_id: Optional[str] = None) -> str:
        assert Path(dataset_path).is_file(), f"{dataset_path} is not a file. Please make sure it is a file"
        assert is_jsonl_file_valid(dataset_path), f"This JSONL file {dataset_path} is not valid"
        
        # First upload dataset
        response = do_request(
            url="{}/v1/finetunings/datasets/".format(
                Config.MODELS_API_BASE_URL_X_BACKEND
            ),
            files={
                "file": open(str(dataset_path), 'rb')
            },
            http_method="post",
            workspace_id=workspace_id
        )
        
        dataset_id = response.json()["data"]
        
        return dataset_id
    
    @classmethod
    def create_finetuning(cls, finetuning: ModelsAPIFinetuning, reason: str = "", workspace_id: Optional[str] = None) -> ModelsAPIFinetuning: 
        assert finetuning.model_family is not None, "The model_family cannot be None"
                
        # Then create the finetuning              
        finetuning_dict = finetuning.dict()
        
        response = do_request(
            url="{}/v1/finetunings/".format(
                Config.MODELS_API_BASE_URL_X_BACKEND
            ),
            params={
                "reason": reason
            },
            http_method="post",
            json_data=finetuning_dict,
            workspace_id=workspace_id
        )
        
        returned_finetuning_dict = response.json()["data"]
        returned_finetuning = ModelsAPIFinetuning.parse_obj(returned_finetuning_dict)
        
        return returned_finetuning
    
    @classmethod
    def get_deployments(cls, workspace_id: Optional[str] = None) -> List[ModelsAPIDeployment]:        
        response = do_request(
            url="{}/v1/deployments/".format(
                Config.MODELS_API_BASE_URL_X_BACKEND
            ),
            http_method="get",
            workspace_id=workspace_id
        )
        
        list_deployment_dicts = response.json()["data"]
        deployments = []
        
        for deployment_dict in list_deployment_dicts:
            deployment = ModelsAPIDeployment.parse_obj(deployment_dict)
            deployments.append(deployment)
            
        return deployments
    
    @classmethod
    def get_deployment_by_name(cls, deployment_name: str, workspace_id: Optional[str] = None) -> ModelsAPIDeployment:        
        response = do_request(
            url="{}/v1/deployments/{}".format(
                Config.MODELS_API_BASE_URL_X_BACKEND,
                deployment_name
            ),
            http_method="get",
            workspace_id=workspace_id
        )
        
        deployment_dict = response.json()["data"]
        deployment = ModelsAPIDeployment.parse_obj(deployment_dict)
        
        return deployment

    @classmethod
    def delete_deployment(cls, deployment_name: str, reason: str = "", workspace_id: Optional[str] = None) -> ModelsAPIDeployment:
        response = do_request(
            url="{}/v1/deployments/{}".format(
                Config.MODELS_API_BASE_URL_X_BACKEND,
                deployment_name
            ),
            params={
                "hard_delete": True,
                "reason": reason
            },
            http_method="delete",
            workspace_id=workspace_id
        )
        
        deployment_dict = response.json()["data"]
        deployment = ModelsAPIDeployment.parse_obj(deployment_dict)
        return deployment
    
    @classmethod
    def create_deployment(cls, deployment: ModelsAPIDeployment, reason: str = "", workspace_id: Optional[str] = None) -> ModelsAPIDeployment:        
        deployment_dict = deployment.dict()
        
        response = do_request(
            url="{}/v1/deployments/".format(
                Config.MODELS_API_BASE_URL_X_BACKEND
            ),
            params={
                "reason": reason
            },
            http_method="post",
            json_data=deployment_dict,
            workspace_id=workspace_id
        )
        
        returned_deployment_dict = response.json()["data"]
        returned_deployment = ModelsAPIDeployment.parse_obj(returned_deployment_dict)
        
        return returned_deployment
       
    @classmethod
    def is_deployment_ready(cls, deployment_name: str, workspace_id: Optional[str] = None):
        deployment = cls.get_deployment_by_name(deployment_name=deployment_name, workspace_id=workspace_id)
            
        response = requests.get(
            url=deployment.inference.is_ready_endpoint,
            headers={
                "x-api-key": deployment.inference.api_key
            }
        )
        
        if response.status_code == 200:
            is_deployment_ready = response.json().get("ready")
            
            if is_deployment_ready:
                return True
            
        return False
                        
    @classmethod
    def wait_until_deployment_is_ready(
        cls, 
        deployment_name: str, 
        timeout: int = 1000, 
        workspace_id: Optional[str] = None
    ):
        sleep_time = 10
        total_time = 0
        while not cls.is_deployment_ready(deployment_name=deployment_name, workspace_id=workspace_id) and total_time < timeout:
            time.sleep(sleep_time)
            total_time += sleep_time
            
    @classmethod
    def get_models(cls, workspace_id: Optional[str] = None) -> List[ModelsAPIModel]:        
        response = do_request(
            url="{}/v1/models/".format(
                Config.MODELS_API_BASE_URL_X_BACKEND
            ),
            http_method="get",
            workspace_id=workspace_id
        )
        
        list_model_dicts = response.json()["data"]
        models = []
        
        for deployment_dict in list_model_dicts:
            model = ModelsAPIModel.parse_obj(deployment_dict)
            models.append(model)
            
        return models
    
    @classmethod
    def get_model_by_name(cls, model_name: str, workspace_id: Optional[str] = None) -> ModelsAPIModel:        
        response = do_request(
            url="{}/v1/models/{}".format(
                Config.MODELS_API_BASE_URL_X_BACKEND,
                model_name
            ),
            http_method="get",
            workspace_id=workspace_id
        )
        
        model_dict = response.json()["data"]
        model = ModelsAPIModel.parse_obj(model_dict)
        
        return model
    
    @classmethod
    def delete_model(cls, model_name: str, reason: str = "", workspace_id: Optional[str] = None) -> ModelsAPIModel:
        response = do_request(
            url="{}/v1/models/{}".format(
                Config.MODELS_API_BASE_URL_X_BACKEND,
                model_name
            ),
            params={
                "hard_delete": True,
                "reason": reason
            },
            http_method="delete",
            workspace_id=workspace_id
        )
        
        model_dict = response.json()["data"]
        model = ModelsAPIModel.parse_obj(model_dict)
        return model


class OnPremiseModelsAPIClient:
    @classmethod
    def get_finetunings(cls, workspace_id: Optional[str] = None) -> List[OnPremiseModelsAPIFinetuning]:        
        response = do_request(
            url="{}/v1/finetunings/".format(
                Config.ON_PREMISE_MODELS_API_BASE_URL_X_BACKEND
            ),
            http_method="get",
            workspace_id=workspace_id
        )
        
        list_finetunings_dicts = response.json()["data"]
        deployments = []
        
        for deployment_dict in list_finetunings_dicts:
            deployment = OnPremiseModelsAPIFinetuning.parse_obj(deployment_dict)
            deployments.append(deployment)
            
        return deployments
    
    @classmethod
    def get_finetuning_by_name(cls, finetuning_name: str, workspace_id: Optional[str] = None) -> OnPremiseModelsAPIFinetuning:        
        response = do_request(
            url="{}/v1/finetunings/{}".format(
                Config.ON_PREMISE_MODELS_API_BASE_URL_X_BACKEND,
                finetuning_name
            ),
            http_method="get",
            workspace_id=workspace_id
        )
        
        finetuning_dict = response.json()["data"]
        finetuning = OnPremiseModelsAPIFinetuning.parse_obj(finetuning_dict)
        
        return finetuning
    
    @classmethod
    def delete_finetuning(cls, finetuning_name: str, reason: str = "", workspace_id: Optional[str] = None) -> OnPremiseModelsAPIFinetuning:
        response = do_request(
            url="{}/v1/finetunings/{}".format(
                Config.ON_PREMISE_MODELS_API_BASE_URL_X_BACKEND,
                finetuning_name
            ),
            params={
                "hard_delete": True,
                "reason": reason
            },
            http_method="delete",
            workspace_id=workspace_id
        )
        
        finetuning_dict = response.json()["data"]
        finetuning = OnPremiseModelsAPIFinetuning.parse_obj(finetuning_dict)
        return finetuning
    
    @classmethod
    def create_finetuning(cls, finetuning: OnPremiseModelsAPIFinetuning, reason: str = "", workspace_id: Optional[str] = None) -> OnPremiseModelsAPIFinetuning: 
        assert finetuning.model_family is not None, "The model_family cannot be None"
                
        # Then create the finetuning              
        finetuning_dict = finetuning.dict()
        
        response = do_request(
            url="{}/v1/finetunings/".format(
                Config.ON_PREMISE_MODELS_API_BASE_URL_X_BACKEND
            ),
            params={
                "reason": reason
            },
            http_method="post",
            json_data=finetuning_dict,
            workspace_id=workspace_id
        )
        
        returned_finetuning_dict = response.json()["data"]
        returned_finetuning = OnPremiseModelsAPIFinetuning.parse_obj(returned_finetuning_dict)
        
        return returned_finetuning
    
    @classmethod
    def get_deployments(cls, workspace_id: Optional[str] = None) -> List[OnPremiseModelsAPIDeployment]:        
        response = do_request(
            url="{}/v1/deployments/".format(
                Config.ON_PREMISE_MODELS_API_BASE_URL_X_BACKEND
            ),
            http_method="get",
            workspace_id=workspace_id
        )
        
        list_deployment_dicts = response.json()["data"]
        deployments = []
        
        for deployment_dict in list_deployment_dicts:
            deployment = OnPremiseModelsAPIDeployment.parse_obj(deployment_dict)
            deployments.append(deployment)
            
        return deployments
    
    @classmethod
    def get_deployment_by_name(cls, deployment_name: str, workspace_id: Optional[str] = None) -> OnPremiseModelsAPIDeployment:        
        response = do_request(
            url="{}/v1/deployments/{}".format(
                Config.ON_PREMISE_MODELS_API_BASE_URL_X_BACKEND,
                deployment_name
            ),
            http_method="get",
            workspace_id=workspace_id
        )
        
        deployment_dict = response.json()["data"]
        deployment = OnPremiseModelsAPIDeployment.parse_obj(deployment_dict)
        
        return deployment

    @classmethod
    def delete_deployment(cls, deployment_name: str, reason: str = "", workspace_id: Optional[str] = None) -> OnPremiseModelsAPIDeployment:
        response = do_request(
            url="{}/v1/deployments/{}".format(
                Config.ON_PREMISE_MODELS_API_BASE_URL_X_BACKEND,
                deployment_name
            ),
            params={
                "hard_delete": True,
                "reason": reason
            },
            http_method="delete",
            workspace_id=workspace_id
        )
        
        deployment_dict = response.json()["data"]
        deployment = OnPremiseModelsAPIDeployment.parse_obj(deployment_dict)
        return deployment
    
    @classmethod
    def create_deployment(cls, deployment: OnPremiseModelsAPIDeployment, reason: str = "", workspace_id: Optional[str] = None) -> OnPremiseModelsAPIDeployment:        
        deployment_dict = deployment.dict()
        
        response = do_request(
            url="{}/v1/deployments/".format(
                Config.ON_PREMISE_MODELS_API_BASE_URL_X_BACKEND
            ),
            params={
                "reason": reason
            },
            http_method="post",
            json_data=deployment_dict,
            workspace_id=workspace_id
        )
        
        returned_deployment_dict = response.json()["data"]
        returned_deployment = OnPremiseModelsAPIDeployment.parse_obj(returned_deployment_dict)
        
        return returned_deployment
       
    @classmethod
    def is_deployment_ready(cls, deployment_name: str, workspace_id: Optional[str] = None):
        deployment = cls.get_deployment_by_name(deployment_name=deployment_name, workspace_id=workspace_id)
            
        response = requests.get(
            url=deployment.inference.is_ready_endpoint,
            headers={
                "x-api-key": deployment.inference.api_key
            }
        )
        
        if response.status_code == 200:
            is_deployment_ready = response.json().get("ready")
            
            if is_deployment_ready:
                return True
            
        return False
                        
    @classmethod
    def wait_until_deployment_is_ready(
        cls, 
        deployment_name: str, 
        timeout: int = 1000, 
        workspace_id: Optional[str] = None
    ):
        sleep_time = 10
        total_time = 0
        while not cls.is_deployment_ready(deployment_name=deployment_name, workspace_id=workspace_id) and total_time < timeout:
            time.sleep(sleep_time)
            total_time += sleep_time
