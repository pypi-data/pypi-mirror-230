import click

from xcloud.__about__ import __version__
from xcloud.cli.configure import configure_command


@click.group(
    context_settings={'help_option_names': ['-h', '--help']}, 
    invoke_without_command=True
)
@click.version_option(version=__version__, prog_name='xCloud')
@click.pass_context
def xcloud(ctx: click.Context):
    pass

xcloud.add_command(configure_command)
