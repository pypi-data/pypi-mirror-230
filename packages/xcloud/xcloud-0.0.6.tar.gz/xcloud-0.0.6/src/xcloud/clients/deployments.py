from xcloud.utils.requests_utils import do_request
from xcloud.config import Config
from xcloud.dtypes.deployments import Deployment
from xcloud.dtypes.shared import Status
from typing import List, Optional
import requests
import time


class DeploymentsClient:
    
    @classmethod
    def get_deployments(cls, workspace_id: Optional[str] = None) -> List[Deployment]:        
        response = do_request(
            url="{}/v1/deployments/".format(
                Config.DEPLOYMENTS_BASE_URL_X_BACKEND
            ),
            http_method="get",
            workspace_id=workspace_id
        )
        
        list_deployment_dicts = response.json()["data"]
        deployments = []
        
        for deployment_dict in list_deployment_dicts:
            deployment = Deployment.parse_obj(deployment_dict)
            deployments.append(deployment)
            
        return deployments
    
    @classmethod
    def get_deployment_by_name(cls, deployment_name: str, workspace_id: Optional[str] = None) -> Deployment:        
        response = do_request(
            url="{}/v1/deployments/{}".format(
                Config.DEPLOYMENTS_BASE_URL_X_BACKEND,
                deployment_name
            ),
            http_method="get",
            workspace_id=workspace_id
        )
        
        deployment_dict = response.json()["data"]
        deployment = Deployment.parse_obj(deployment_dict)
        
        return deployment
    
    @classmethod
    def get_logs(cls, deployment_name: str, workspace_id: Optional[str] = None) -> List[Deployment]:        
        response = do_request(
            url="{}/v1/deployments/{}/logs".format(
                Config.DEPLOYMENTS_BASE_URL_X_BACKEND,
                deployment_name
            ),
            http_method="get",
            workspace_id=workspace_id
        )
        
        logs = response.json()["data"]
        
        return logs
    
    @classmethod
    def cancel_deployment(cls, deployment_name: str, reason: str = "", workspace_id: Optional[str] = None) -> Deployment:
        response = do_request(
            url="{}/v1/deployments/{}".format(
                Config.DEPLOYMENTS_BASE_URL_X_BACKEND,
                deployment_name
            ),
            params={
                "hard_delete": False,
                "reason": reason
            },
            http_method="delete",
            workspace_id=workspace_id
        )
        
        deployment_dict = response.json()["data"]
        deployment = Deployment.parse_obj(deployment_dict)
        return deployment
    
    @classmethod
    def archive_deployment(cls, deployment_name: str, reason: str = "", workspace_id: Optional[str] = None) -> Deployment:
        response = do_request(
            url="{}/v1/deployments/{}".format(
                Config.DEPLOYMENTS_BASE_URL_X_BACKEND,
                deployment_name
            ),
            params={
                "hard_delete": False,
                "archive": True,
                "reason": reason
            },
            http_method="delete",
            workspace_id=workspace_id
        )
        
        deployment_dict = response.json()["data"]
        deployment = Deployment.parse_obj(deployment_dict)
        return deployment
    
    @classmethod
    def delete_deployment(cls, deployment_name: str, reason: str = "", workspace_id: Optional[str] = None) -> Deployment:
        response = do_request(
            url="{}/v1/deployments/{}".format(
                Config.DEPLOYMENTS_BASE_URL_X_BACKEND,
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
        deployment = Deployment.parse_obj(deployment_dict)
        return deployment
    
    @classmethod
    def create_deployment(cls, deployment: Deployment, reason: str = "", workspace_id: Optional[str] = None) -> Deployment:        
        deployment_dict = deployment.dict()
        
        response = do_request(
            url="{}/v1/deployments/".format(
                Config.DEPLOYMENTS_BASE_URL_X_BACKEND
            ),
            params={
                "reason": reason
            },
            http_method="post",
            json_data=deployment_dict,
            workspace_id=workspace_id
        )
        
        returned_deployment_dict = response.json()["data"]
        returned_deployment = Deployment.parse_obj(returned_deployment_dict)
        
        return returned_deployment
       
    @classmethod
    def is_deployment_ready(cls, deployment_name: str, workspace_id: Optional[str] = None):
        deployment = cls.get_deployment_by_name(deployment_name=deployment_name, workspace_id=workspace_id)
                
        return deployment.status == Status.RUNNING
                        
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