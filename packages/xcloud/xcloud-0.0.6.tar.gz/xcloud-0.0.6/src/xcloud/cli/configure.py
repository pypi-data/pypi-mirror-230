import click
from typing import Optional

from xcloud.config import Config
from xcloud.utils.logging import configure_logger
from xcloud.utils.config_utils import overwrite_config
from xcloud.utils.validations import is_config_valid

logger = configure_logger(__name__)

@click.command(name="configure")
@click.option('-k', '--api_key', hide_input=True, prompt='[*] Your API key')
@click.option('-w', '--default_workspace', prompt='[*] Your default workspace')
def configure_command(api_key: Optional[str], default_workspace: Optional[str]):    
    xcloud_config = {
        "XCLOUD_API_KEY": api_key,
        "XCLOUD_DEFAULT_WORKSPACE": default_workspace
    }
        
    click.secho('[*] Validating your data...', fg='white', bold=True)
    is_valid = is_config_valid(api_key=api_key, workspace_id=default_workspace)
    if not is_valid:
        return click.secho('[!] Your configuration is not valid. Make sure to provide the correct API Key and default workspace ID. If the problem persists contact support.', fg='red', bold=True)
    
    overwrite_config(xcloud_config)
    click.secho('[+] Configuration added successfully', fg='green', bold=True)