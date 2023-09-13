import uuid
from pathlib import Path
from typing import List

import click
import yaml
from click import Context
from click.types import UUID
from sifflet_sdk.client.model.as_code_workspace_dto import AsCodeWorkspaceDto
from sifflet_sdk.client.model.workspace_apply_response_dto import WorkspaceApplyResponseDto
from rich.console import Console
from rich.syntax import Syntax
from sifflet_sdk.code.workspace.service import WorkspaceService
from sifflet_sdk.constants import SIFFLET_CONFIG_CTX


@click.group()
def workspace():
    """Manage and apply workspaces."""


@workspace.command()
@click.option("--file", "-f", "file_name", required=True, type=click.Path(), help="Path of the Workspace YAML file")
@click.option("--name", "-n", "name", required=True, type=str, help="Name of the workspace")
@click.pass_context
def init(ctx: Context, file_name: str, name: str):
    """
    Creates a new Workspace YAML file locally.
    """
    sifflet_config = ctx.obj[SIFFLET_CONFIG_CTX]
    workspace_service = WorkspaceService(sifflet_config)
    workspace_service.initialize_workspace(Path(file_name), name)


@workspace.command()
@click.pass_context
def list(ctx: Context):
    """
    List all workspaces.
    """
    sifflet_config = ctx.obj[SIFFLET_CONFIG_CTX]
    workspace_service = WorkspaceService(sifflet_config)
    workspace_apply_response: List[AsCodeWorkspaceDto] = workspace_service.list_workspaces()
    # Print list of workspaces
    console = Console()
    for workspace in workspace_apply_response:
        if workspace.description:
            console.print(f" - [bold]{workspace.id}[/bold] - {workspace.name} ({workspace.description})")
        else:
            console.print(f" - [bold]{workspace.id}[/bold] - {workspace.name}")


@workspace.command()
@click.option("--id", "id", required=True, type=UUID, help="ID of the workspace")
@click.option("--dry-run", "dry_run", is_flag=True, help="Only return the plan for the changes without executing them")
@click.pass_context
def delete(ctx: Context, id: uuid.UUID, dry_run: bool):
    """
    Deletes a workspace.
    """
    sifflet_config = ctx.obj[SIFFLET_CONFIG_CTX]
    workspace_service = WorkspaceService(sifflet_config)
    workspace_apply_response: WorkspaceApplyResponseDto = workspace_service.delete_workspace(id, dry_run)
    print_response(workspace_apply_response)


@workspace.command()
@click.option(
    "--file",
    "-f",
    "workspace_file_name",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    help="Path of the Workspace YAML file",
)
@click.option("--dry-run", "dry_run", is_flag=True, help="Only return the plan for the changes without executing them")
@click.option(
    "--force-delete",
    "force_delete",
    is_flag=True,
    help="Allow deleting the objects in the workspace if they are removed from the workspace files",
)
@click.pass_context
def apply(ctx: Context, workspace_file_name: str, dry_run: bool, force_delete: bool):
    """
    Apply the specified workspace.
    """
    sifflet_config = ctx.obj[SIFFLET_CONFIG_CTX]
    workspace_service = WorkspaceService(sifflet_config)
    workspace_apply_response: WorkspaceApplyResponseDto = workspace_service.apply_workspace(
        Path(workspace_file_name), dry_run, force_delete
    )
    print_response(workspace_apply_response)


def print_response(response: WorkspaceApplyResponseDto) -> None:
    console = Console()
    syntax = Syntax(yaml.dump(response.to_dict(), sort_keys=False), "yaml")
    console.print(syntax)
