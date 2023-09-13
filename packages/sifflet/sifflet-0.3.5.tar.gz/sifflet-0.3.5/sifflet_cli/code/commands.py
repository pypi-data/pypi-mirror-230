import click

from sifflet_cli.code.workspace.commands import workspace


@click.group()
def code():
    """Manage Sifflet resources as code."""


code.add_command(workspace)
