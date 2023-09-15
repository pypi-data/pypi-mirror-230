from xcloud.utils.requests_utils import do_request
from xcloud.config import Config
from xcloud.dtypes.notebooks import Notebook
from typing import List, Optional
import requests
from xcloud.dtypes.shared import Status
import time


class NotebooksClient:
    
    @classmethod
    def get_notebooks(cls, workspace_id: Optional[str] = None) -> List[Notebook]:        
        response = do_request(
            url="{}/v1/notebooks/".format(
                Config.NOTEBOOKS_BASE_URL_X_BACKEND
            ),
            http_method="get",
            workspace_id=workspace_id
        )
        
        list_notebook_dicts = response.json()["data"]
        notebooks = []
        
        for notebook_dict in list_notebook_dicts:
            notebook = Notebook.parse_obj(notebook_dict)
            notebooks.append(notebook)
            
        return notebooks
    
    @classmethod
    def get_notebook_by_name(cls, notebook_name: str, workspace_id: Optional[str] = None) -> Notebook:        
        response = do_request(
            url="{}/v1/notebooks/{}".format(
                Config.NOTEBOOKS_BASE_URL_X_BACKEND,
                notebook_name
            ),
            http_method="get",
            workspace_id=workspace_id
        )
        
        notebook_dict = response.json()["data"]
        notebook = Notebook.parse_obj(notebook_dict)
        
        return notebook
    
    @classmethod
    def cancel_notebook(cls, notebook_name: str, reason: str = "", workspace_id: Optional[str] = None) -> Notebook:
        response = do_request(
            url="{}/v1/notebooks/{}".format(
                Config.NOTEBOOKS_BASE_URL_X_BACKEND,
                notebook_name
            ),
            params={
                "hard_delete": False,
                "reason": reason
            },
            http_method="delete",
            workspace_id=workspace_id
        )
        
        notebook_dict = response.json()["data"]
        notebook = Notebook.parse_obj(notebook_dict)
        return notebook
    
    @classmethod
    def archive_notebook(cls, notebook_name: str, reason: str = "", workspace_id: Optional[str] = None) -> Notebook:
        response = do_request(
            url="{}/v1/notebooks/{}".format(
                Config.NOTEBOOKS_BASE_URL_X_BACKEND,
                notebook_name
            ),
            params={
                "hard_delete": False,
                "archive": True,
                "reason": reason
            },
            http_method="delete",
            workspace_id=workspace_id
        )
        
        notebook_dict = response.json()["data"]
        notebook = Notebook.parse_obj(notebook_dict)
        return notebook
    
    @classmethod
    def delete_notebook(cls, notebook_name: str, reason: str = "", workspace_id: Optional[str] = None) -> Notebook:
        response = do_request(
            url="{}/v1/notebooks/{}".format(
                Config.NOTEBOOKS_BASE_URL_X_BACKEND,
                notebook_name
            ),
            params={
                "hard_delete": True,
                "reason": reason
            },
            http_method="delete",
            workspace_id=workspace_id
        )
        
        notebook_dict = response.json()["data"]
        notebook = Notebook.parse_obj(notebook_dict)
        return notebook
    
    @classmethod
    def create_notebook(cls, notebook: Notebook, reason: str = "", workspace_id: Optional[str] = None) -> Notebook:        
        notebook_dict = notebook.dict()
        
        response = do_request(
            url="{}/v1/notebooks/".format(
                Config.NOTEBOOKS_BASE_URL_X_BACKEND
            ),
            params={
                "reason": reason
            },
            http_method="post",
            json_data=notebook_dict,
            workspace_id=workspace_id
        )
        
        returned_notebook_dict = response.json()["data"]
        returned_notebook = Notebook.parse_obj(returned_notebook_dict)
        
        return returned_notebook
       
    @classmethod
    def is_notebook_ready(cls, notebook_name: str, workspace_id: Optional[str] = None):
        notebook = cls.get_notebook_by_name(notebook_name=notebook_name, workspace_id=workspace_id)
            
        response = requests.get(
            url=notebook.access_details.full_url
        )
        
        return response.status_code == 200
                        
    @classmethod
    def wait_until_notebook_is_ready(
        cls, 
        notebook_name: str, 
        timeout: int = 1000, 
        workspace_id: Optional[str] = None
    ):
        sleep_time = 10
        total_time = 0
        while not cls.is_notebook_ready(notebook_name=notebook_name, workspace_id=workspace_id) and total_time < timeout:
            time.sleep(sleep_time)
            total_time += sleep_time