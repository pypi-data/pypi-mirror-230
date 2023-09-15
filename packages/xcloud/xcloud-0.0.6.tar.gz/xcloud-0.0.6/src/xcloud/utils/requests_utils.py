import requests
from requests.adapters import HTTPAdapter, Retry
import urllib3
from xcloud.utils.config_utils import get_api_key, get_default_workspace
from xcloud.config import Config
from xcloud.utils.logging import configure_logger
from typing import Optional

logger = configure_logger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def do_request(
    url, 
    http_method, 
    json_data=None, 
    headers=None,
    params=None,
    files=None,
    xcloud_auth: bool = True,
    workspace_id: Optional[str] = None,
    throw_error: bool = True,
    timeout: int = 30
):
    headers = {} if headers is None else headers
    
    if xcloud_auth:
        api_key = get_api_key()

    assert api_key is not None, "We were not able to find your API key. To use the CLI or the Python client you need one. You can get an API Key in your profile. Then run the command `xcloud configure` or use the environment variable XCLOUD_API_KEY"
    headers['x-api-key'] = api_key
        
    if workspace_id is None:
        workspace_id = get_default_workspace()
        
    assert workspace_id is not None, "The workspace_id cannot be None. Configure your workspace running the command `xcloud configure` or use the environment variable XCLOUD_DEFAULT_WORKSPACE"
    
    headers['workspaceId'] = workspace_id
        
    session = requests.Session()
    retries = Retry(
        total=5,
        status_forcelist=[ 500, 502, 503, 504 ]
    )
    
    session.mount("http://", HTTPAdapter(max_retries=retries))
        
    params_fn = {
        "url": url, 
        "json": json_data,
        "files": files,
        "timeout": timeout,
        "headers": headers,
        "verify": False,
        "params": params
    }
        
    if Config.DEBUG:
        logger.debug(f"Request params: {params_fn}")
    
    if http_method == "get":
        response = session.get(**params_fn)
    elif http_method == "post":
        response = session.post(**params_fn)
    elif http_method == "patch":
        response = session.patch(**params_fn)
    elif http_method == "delete":
        response = session.delete(**params_fn)
    elif http_method == "put":
        response = session.put(**params_fn)
    
    error = False
    try:
        response.raise_for_status()
    except Exception as ex:
        error = True
        
    if error and throw_error:
        if 'application/json' in response.headers.get('Content-Type', ''):
            raise ValueError(response.json()["message"])
        else:
            raise ValueError(response.text)
    
    return response