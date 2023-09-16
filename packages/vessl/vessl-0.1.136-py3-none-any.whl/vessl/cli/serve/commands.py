"""
Serving command definition and delegation.
"""
import sys
from typing import List, Optional, TextIO

import click
import yaml

from openapi_client.models import ResponseModelServiceInfo
from openapi_client.models.response_kernel_cluster import ResponseKernelCluster
from vessl import vessl_api
from vessl.cli._base import VesslCommand, VesslGroup
from vessl.cli.serve.util import (
    list_http_ports,
    print_gateway,
    print_revision,
    validate_port_choice,
)
from vessl.serving import (
    create_revision_from_yaml,
    list_revisions,
    list_servings,
    read_gateway,
    read_revision,
    update_gateway_for_revision,
    update_gateway_from_yaml,
)
from vessl.util.exception import VesslApiException

from .command_options import (
    enable_gateway_if_off_option,
    serving_name_option,
    update_gateway_option,
    update_gateway_port_option,
    update_gateway_weight_option,
)

cli = VesslGroup("serve")


@cli.command("list", cls=VesslCommand)
def serving_list():
    """
    List servings in current organization.
    """
    servings: List[ResponseModelServiceInfo] = list_servings(
        organization=vessl_api.organization.name
    ).results

    print(f"{len(servings)} serving(s) found.\n")
    for serving in servings:
        kernel_cluster: ResponseKernelCluster = serving.kernel_cluster
        status: str = serving.status  # "ready", "running", "error"

        print(f"{serving.name} (cluster {kernel_cluster.name}): status {status.capitalize()}")


@cli.group("revision")
def cli_revision():
    """
    Root command for revision-related commands.
    """
    pass


@cli_revision.command("create", cls=VesslCommand)
@serving_name_option
@click.option(
    "-f",
    "--file",
    type=click.File("r"),
    required=True,
    help="Path to YAML file for serving revision definition.",
)
@update_gateway_option
@enable_gateway_if_off_option
@update_gateway_weight_option
@update_gateway_port_option
def revision_create_with_yaml(
    serving: ResponseModelServiceInfo,
    file: TextIO,
    update_gateway: bool,
    enable_gateway_if_off: bool,
    update_gateway_weight: Optional[int] = None,
    update_gateway_port: Optional[int] = None,
):
    """
    Create serving revision with spec written in YAML.
    """
    if not update_gateway and (
        update_gateway_weight is not None or update_gateway_port is not None
    ):
        print("Cannot specify traffic weight or port when not updating gateway.")
        sys.exit(1)

    yaml_body = file.read()
    yaml_obj = yaml.safe_load(yaml_body)

    if update_gateway:
        # Do as much validation as possible before actually creating revision.
        # weight check
        if update_gateway_weight is None:
            update_gateway_weight = 100
        elif not 1 <= update_gateway_weight <= 100:
            print(f"Invalid weight: {update_gateway_weight}% (must be between 1 and 100)")
            sys.exit(1)

        # port check
        if update_gateway_port is None:
            http_ports = list_http_ports(yaml_obj)
            if len(http_ports) != 1:
                print(
                    "Error: port for gateway was not specified, and could not automatically "
                    "determine which port to use.\n"
                    f"{len(http_ports)} port(s) was found: " + ", ".join(map(str, http_ports))
                )
                sys.exit(1)
            update_gateway_port = http_ports[0]
            print(f"Automatically choosing port {update_gateway_port} for gateway.")
        elif not 1 <= update_gateway_port <= 65535:
            print(f"Invalid port: {update_gateway_port}")
            sys.exit(1)
        else:
            validate_port_choice(yaml_obj, update_gateway_port)

        # gateway status check
        if not enable_gateway_if_off:
            gateway_current = read_gateway(
                organization=vessl_api.organization.name, serving_name=serving.name
            )
            if not gateway_current.enabled:
                print("Cannot update gateway because it is not enabled. Please enable it first.")
                print("NOTE (current status of gateway):")
                print_gateway(gateway_current)
                sys.exit(1)

    revision = create_revision_from_yaml(
        organization=vessl_api.organization.name, serving_name=serving.name, yaml_body=yaml_body
    )
    print(f"Successfully created revision in serving {serving.name}.\n")
    print_revision(revision)

    if update_gateway:
        gateway_updated = update_gateway_for_revision(
            vessl_api.organization.name,
            serving_name=serving.name,
            revision_number=revision.number,
            port=update_gateway_port,
            weight=update_gateway_weight,
        )
        print(f"Successfully updated gateway for revision #{revision.number}.\n")
        print_gateway(gateway_updated)
    else:
        print(
            "NOTE: Since --update-gateway option was not given, "
            "you cannot currently access this revision via gateway.\n\n"
            "Either use --update-gateway when creating revision, or update gateway manually."
        )


@cli_revision.command("show", cls=VesslCommand)
@serving_name_option
@click.option("--number", "-n", required=True, type=int, help="Number of revision.")
def revision_show(serving: ResponseModelServiceInfo, number: int):
    """
    Show current status and information about a serving revision.
    """
    try:
        revision = read_revision(
            organization=vessl_api.organization.name,
            serving_name=serving.name,
            revision_number=number,
        )
    except VesslApiException as e:
        print(f"Failed to read revision #{number} of serving {serving.name}: {e.message}")
        sys.exit(1)

    print_revision(revision, verbose=True)


@cli_revision.command("list", cls=VesslCommand)
@serving_name_option
def revision_list(serving: ResponseModelServiceInfo):
    """
    List all revisions.
    """
    try:
        revisions = list_revisions(
            organization=vessl_api.organization.name,
            serving_name=serving.name,
        )
    except VesslApiException as e:
        print(f"Failed to list revisions of serving {serving.name}: {e.message}")
        sys.exit(1)

    print(f"{len(revisions)} revision(s) found.\n")

    for i, revision in enumerate(revisions):
        if i > 0:
            print()
        print_revision(revision)


@cli.group("gateway")
def cli_gateway():
    """
    Root command for gateway-related commands.
    """
    pass


@cli_gateway.command("show", cls=VesslCommand)
@serving_name_option
def gateway_show(serving: ResponseModelServiceInfo):
    """
    Show current status of the gateway of a serving.
    """
    try:
        gateway = read_gateway(
            organization=vessl_api.organization.name,
            serving_name=serving.name,
        )
    except VesslApiException as e:
        print(f"Failed to read gateway of serving {serving.name}: {e.message}")
        sys.exit(1)

    print_gateway(gateway)


@cli_gateway.command("update", cls=VesslCommand)
@serving_name_option
@click.option(
    "-f",
    "--file",
    type=click.File("r"),
    required=True,
    help="Path to YAML file for serving revision definition.",
)
def gateway_update_with_yaml(serving: ResponseModelServiceInfo, file: TextIO):
    """
    Update serving gateway with spec written in YAML.
    """
    yaml_body = file.read()

    gateway = update_gateway_from_yaml(
        organization=vessl_api.organization.name, serving_name=serving.name, yaml_body=yaml_body
    )
    print(f"Successfully update gateway of serving {serving.name}.\n")
    print_gateway(gateway)
