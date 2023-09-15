import platform
from enum import Enum
from xcloud.config import Config
from typing import Union, Dict, Any
from pathlib import Path
import tempfile
import json
import uuid
import subprocess
import requests
import shutil
import os
import stat
from xcloud.utils.logging import configure_logger

logger = configure_logger(__name__)


class PlatformType(str, Enum):
    LINUX: str = "linux"
    WINDOWS: str = "windows"
    MACOS: str = "MACOS"

def get_platform() -> PlatformType:
    operative_system = platform.system()
    
    if operative_system == "Linux":
        return PlatformType.LINUX
    
    if operative_system == "Windows":
        return PlatformType.WINDOWS
    
    if operative_system == "Darwin":
        return PlatformType.MACOS

def download_hey(platform: PlatformType):
    download_link = None
    if platform == PlatformType.LINUX:
        download_link = "https://hey-release.s3.us-east-2.amazonaws.com/hey_linux_amd64"
        
    if platform == PlatformType.WINDOWS:
        download_link = "https://hey-release.s3.us-east-2.amazonaws.com/hey_windows_amd64"
        
    if platform == PlatformType.MACOS:
        download_link = "https://hey-release.s3.us-east-2.amazonaws.com/hey_darwin_amd64"
        
    if download_link is None:
        raise ValueError("It was not possible to get your platform. Please, contact xCloud support.")
        
        
    r = requests.get(download_link, verify=False, stream=True)
    r.raw.decode_content = True
    hey_location = str(Config.XCLOUD_ASSETS / "hey")
    
    if not Config.XCLOUD_ASSETS.exists():
        Config.XCLOUD_ASSETS.mkdir(parents=True, exist_ok=True)
    
    with open(hey_location, 'wb') as f:
        shutil.copyfileobj(r.raw, f) 
        
    # Give permissions to the file
    st = os.stat(hey_location)
    os.chmod(hey_location, st.st_mode | stat.S_IEXEC)
        
    return hey_location
    

def benchmark_endpoint(
    url: str,
    json_request_body: Dict[str, Any] = {},
    send_requests_duration: int = 30,
    concurrent_workers: int = 1,
    http_method: str = "POST",
    headers: Dict[str, str] = {},
    timeout_per_request: int = 20,
    output_file: Union[str, Path] = "./benchmarks.csv"
):
    ALLOWED_HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"]
    assert http_method in ALLOWED_HTTP_METHODS, "http_method {} is not allowed. Allowed HTTP methods: {}".format(
        http_method,
        ALLOWED_HTTP_METHODS
    )
    output_file = Path(output_file)
    
    # Download Hey based on the operative system
    operative_system = get_platform()
    hey_location = download_hey(platform=operative_system)
    
    # Save JSON into a file
    temp_json_file_path = str(Path(tempfile.gettempdir()) / "{}.json".format(uuid.uuid4()))
    with open(temp_json_file_path, 'w', encoding='utf-8') as f:
        json.dump(json_request_body, f, ensure_ascii=False, indent=4)
        
    command = [
        hey_location, 
        "-c", 
        str(concurrent_workers),
        "-z",
        "{}s".format(send_requests_duration),
        "-m",
        http_method,
        "-H",
        "Content-Type: application/json",
        "-t",
        str(timeout_per_request),
        "-D",
        str(temp_json_file_path)
    ]
    
    for header_key, header_value in headers.items():
        command.append("-H")
        command.append("{}: {}".format(header_key, header_value))
        
    # Url
    command.append(str(url))
    
    logger.debug("Benchmark command: {}".format(command))
        
    subprocess.run(command)   
