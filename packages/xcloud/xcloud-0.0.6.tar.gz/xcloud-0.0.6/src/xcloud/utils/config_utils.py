import os
import json
from xcloud.config import Config
from typing import Dict


def overwrite_config(xcloud_config: Dict):
    if not Config.XCLOUD_CONFIG_PATH.parent.is_dir():
        Config.XCLOUD_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        
    with open(str(Config.XCLOUD_CONFIG_PATH), 'w', encoding='utf-8') as f:
        json.dump(xcloud_config, f, ensure_ascii=False, indent=4)

def read_config():
    if not Config.XCLOUD_CONFIG_PATH.is_file():
        return {}
        
    with open(Config.XCLOUD_CONFIG_PATH) as f:
        config = json.load(f)
        
    return config

def get_api_key():
    api_key = os.getenv("XCLOUD_API_KEY")
    
    if api_key is None:
        api_key = read_config().get("XCLOUD_API_KEY")
            
    return api_key

def get_default_workspace():
    default_workspace = os.getenv("XCLOUD_DEFAULT_WORKSPACE")
    
    if default_workspace is None:
        default_workspace = read_config().get("XCLOUD_DEFAULT_WORKSPACE")
            
    return default_workspace