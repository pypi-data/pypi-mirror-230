import sys
from datetime import datetime
from datetime import timezone
from typing import Optional

import click
from google.protobuf import timestamp_pb2

from tecton._internals import metadata_service
from tecton._internals.display import Displayable
from tecton.cli import printer
from tecton.cli.command import TectonGroup
from tecton_proto.common.container_image_pb2 import ContainerImage
from tecton_proto.data.remote_compute_environment_pb2 import RemoteEnvironmentStatus
from tecton_proto.remoteenvironmentservice.remote_environment_service_pb2 import CreateRemoteEnvironmentRequest
from tecton_proto.remoteenvironmentservice.remote_environment_service_pb2 import DeleteRemoteEnvironmentsRequest
from tecton_proto.remoteenvironmentservice.remote_environment_service_pb2 import ListRemoteEnvironmentsRequest


@click.command("environment", cls=TectonGroup)
def environment():
    """Manage Environments for ODFV Execution"""


@environment.command("list-all")
def list_all():
    """List all available Python Environments"""
    remote_environments = _list_environments()
    _display_environments(remote_environments)


@environment.command("list")
@click.option("--id", help="Environment Id", required=False, type=str)
@click.option("--name", help="Environment Name", required=False, type=str)
def list(id: Optional[str] = None, name: Optional[str] = None):
    """List Python Environment(s) matching a name or an ID"""
    if not id and not name:
        remote_environments = _list_environments()
        _display_environments(remote_environments)
    else:
        identifier = name if name is not None else id
        by_name = name is not None
        remote_environments = _list_environments(identifier=identifier, by_name=by_name)
        _display_environments(remote_environments)


@environment.command("create")
@click.option("-n", "--name", help="Environment name", required=True, type=str)
@click.option("-d", "--description", help="Environment description", required=True, type=str)
@click.option("-i", "--image-uri", help="Image URI. This functionality is in Private Preview.", required=True, type=str)
def create(name: str, description: str, image_uri: str):
    """Create a custom Python Environment with a name, description and a Docker Image URI. Disclaimer: This
    functionality is in Private Preview. Please contact Tecton Support for a trial"""
    resp = _create_environment(name, description, image_uri)
    _display_environments([resp.remote_environment])


# Enable environment deletion in 0.8
'''
@environment.command("delete")
@click.option("--id", help="Environment ID", required=False, type=str)
@click.option("--name", help="Environment Name", required=False, type=str)
def delete(id: Optional[str] = None, name: Optional[str] = None):
    """Delete an existing custom Python Environment by name or an ID"""
    if id is None and name is None:
        printer.safe_print("At least one of `id` or `name` must be provided", file=sys.stderr)
        sys.exit(1)

    identifier = name if name is not None else id
    by_name = name is not None
    environments = _list_environments(identifier=identifier, by_name=by_name)
    if not environments:
        printer.safe_print(
            f"No matching environments found for: {identifier}. Please verify available environments using the `list_all` command",  file=sys.stderr
        )
    elif len(environments) > 1:
        printer.safe_print(
            f"No matching environment found for: {identifier}. Did you mean one of the following environment(s)? \n\n", file=sys.stderr
        )
        _display_environments(environments)
    else:
        environment_to_delete = environments[0]
        confirmation_text = f"Are you sure you want to delete environment {environment_to_delete.name}? (y/n) :"
        confirmation = input(confirmation_text).lower().strip()
        if confirmation == "y":
            try:
                _delete_environment(env_id=environment_to_delete.id)
                printer.safe_print(f"Successfully deleted environment: {identifier}")
            except Exception as e:
                printer.safe_print(f"Failed to delete. error = {str(e)}, type= {type(e).__name__}")
        else:
            printer.safe_print(f"Cancelled deletion for environment: {identifier}")
'''


def _display_environments(environments: list):
    headings = ["Id", "Name", "Status", "Created At", "Updated At"]
    display_table(
        headings,
        [
            (
                i.id,
                i.name,
                RemoteEnvironmentStatus.Name(i.status),
                _timestamp_to_string(i.created_at),
                _timestamp_to_string(i.updated_at),
            )
            for i in environments
        ],
    )


def display_table(headings, ws_roles):
    table = Displayable.from_table(headings=headings, rows=ws_roles, max_width=0)
    # Align columns in the middle horizontally
    table._text_table.set_cols_align(["c" for _ in range(len(headings))])
    printer.safe_print(table)


def _create_environment(name: str, description: str, image_uri):
    try:
        req = CreateRemoteEnvironmentRequest()
        req.name = name
        req.description = description

        image_info = ContainerImage()
        image_info.image_uri = image_uri

        req.image_info.CopyFrom(image_info)

        return metadata_service.instance().CreateRemoteEnvironment(req)
    except PermissionError as e:
        printer.safe_print(
            "The user is not authorized to create environment(s) in Tecton. Please reach out to your Admin to complete this "
            "action",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        printer.safe_print(f"Failed to create environment: {e}", file=sys.stderr)
        sys.exit(1)


def _delete_environment(env_id: str):
    try:
        req = DeleteRemoteEnvironmentsRequest()
        req.ids.append(env_id)
        return metadata_service.instance().DeleteRemoteEnvironments(req)
    except PermissionError as e:
        printer.safe_print(
            "The user is not authorized to perform environment deletion. Please reach out to your Admin to complete this action",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        printer.safe_print(f"Failed to delete environment: {e}", file=sys.stderr)
        sys.exit(1)


def _list_environments(identifier: Optional[str] = None, by_name: bool = False):
    try:
        req = ListRemoteEnvironmentsRequest()
        response = metadata_service.instance().ListRemoteEnvironments(req)

        if identifier is None:
            return response.remote_environments

        if by_name:
            environments = [env for env in response.remote_environments if identifier in env.name]
            error_message = f"Unable to find environments with name: {identifier}"
        else:
            environments = [env for env in response.remote_environments if identifier in env.id]
            error_message = f"Unable to find environment with id: {identifier}"

        if len(environments) < 1:
            printer.safe_print(error_message, file=sys.stderr)
            sys.exit(1)

        return environments

    except Exception as e:
        printer.safe_print(f"Failed to fetch environments: {e}", file=sys.stderr)
        sys.exit(1)


def _timestamp_to_string(value: timestamp_pb2.Timestamp) -> str:
    t = datetime.fromtimestamp(value.ToSeconds())
    return t.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
