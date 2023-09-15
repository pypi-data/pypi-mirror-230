from xcloud.utils.requests_utils import do_request
from xcloud.config import Config
from pathlib import Path
import json
from typing import Union


def is_jsonl_file_valid(file_local_path: Union[Path, str]):
    is_valid = True
    try:
        with open(str(file_local_path), 'r') as json_file:
            json_list = list(json_file)

        for json_str in json_list:
            json.loads(json_str)
    except:
        is_valid = False
        
    return is_valid


# This function is not in config utils to avoid circular imports
def is_config_valid(api_key: str, workspace_id: str):        
    response = do_request(
        url=f"{Config.AUTH_BASE_URL_X_BACKEND}/v1/auth/verify",
        http_method="post",
        headers={
            "x-api-key": api_key,
            # Every user should have at least read permissions
            "x-original-method": "GET",
            "x-original-url": "https://dev.xcloud-api.stochastic.ai/executor/backend/v1/jobs/"
        },
        xcloud_auth=False,
        workspace_id=workspace_id,
        throw_error=False
    )
    
    try:
        response.raise_for_status()
        return True
    except:
        return False