import datetime
import pprint

import click
import tabulate
import yaml

import seaplane_framework.api
from seaplane_framework.api.models import Flow, CarrierInput, CarrierOutput
from seaplane_framework.api.apis.tags import flow_api
from seaplane_framework.cli import util


@click.group()
def flow():
    """Seaplane Flows"""


@flow.command(name="list")
@click.option("--region")
def list_flows(region):
    """list all flows"""
    configuration = util.api_config()
    if not configuration:
        return
    with seaplane_framework.api.ApiClient(configuration) as api_client:
        api_instance = flow_api.FlowApi(api_client)
        query_params = {}
        if region:
            query_params["region"] = region
        try:
            api_response = api_instance.list_flows(
                query_params=query_params,  # type: ignore
            )
            for flow in api_response.body:
                print(flow)
        except seaplane_framework.api.ApiException as e:
            click.echo(
                click.style(
                    "Exception when calling FlowApi->list_flows: %s\n" % e, fg="red"
                )
            )


@flow.command()
@click.argument("flow_name")
@click.option(
    "--flow",
    "-f",
    help="Flow definition JSON/YAML, @ to load a file, @- for stdin",
    required=True,
)
@click.option("--region")
def create(flow_name, flow, region):
    """create a flow"""
    configuration = util.api_config()
    if not configuration:
        return
    flow_definition = util.read_or_return_string(flow)
    # JSON is valid YAML...
    flow_definition_obj = yaml.safe_load(flow_definition)
    with seaplane_framework.api.ApiClient(configuration) as api_client:
        api_instance = flow_api.FlowApi(api_client)
        path_params = {"flow_name": flow_name}
        query_params = {}
        if region:
            query_params["region"] = region
        try:
            api_response = api_instance.create_flow(
                path_params=path_params,  # type: ignore
                query_params=query_params,  # type: ignore
                body=Flow(flow_definition_obj),
            )
        except seaplane_framework.api.ApiException as e:
            click.echo(
                click.style(
                    "Exception when calling FlowApi->create_flow: %s\n" % e, fg="red"
                )
            )


@flow.command()
@click.argument("flow_name")
@click.option("--region")
def delete(flow_name, region):
    """delete a flow"""
    configuration = util.api_config()
    if not configuration:
        return
    with seaplane_framework.api.ApiClient(configuration) as api_client:
        api_instance = flow_api.FlowApi(api_client)
        path_params = {"flow_name": flow_name}
        query_params = {}
        if region:
            query_params["region"] = region
        try:
            api_response = api_instance.delete_flow(
                path_params=path_params,  # type: ignore
                query_params=query_params,  # type: ignore
            )
        except seaplane_framework.api.ApiException as e:
            click.echo(
                click.style(
                    "Exception when calling FlowApi->delete_flow: %s\n" % e, fg="red"
                )
            )


@flow.command()
@click.argument("flow_name")
@click.option("--region")
def details(flow_name, region):
    """show details of flow (configuration)"""
    configuration = util.api_config()
    if not configuration:
        return
    with seaplane_framework.api.ApiClient(configuration) as api_client:
        api_instance = flow_api.FlowApi(api_client)
        path_params = {"flow_name": flow_name}
        query_params = {}
        if region:
            query_params["region"] = region
        try:
            resp = api_instance.get_flow(
                path_params=path_params,  # type: ignore
                query_params=query_params,  # type: ignore
            )
            pprint.pprint(util.map_nested_dicts(resp.body))
        except seaplane_framework.api.ApiException as e:
            click.echo(
                click.style(
                    "Exception when calling FlowApi->get_flow: %s\n" % e, fg="red"
                )
            )


@flow.command(name="list-secrets")
@click.argument("flow_name")
@click.option("--region")
def list_secrets(flow_name, region):
    """list all flow secrets"""
    configuration = util.api_config()
    if not configuration:
        return
    # Enter a context with an instance of the API client
    with seaplane_framework.api.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = flow_api.FlowApi(api_client)

        path_params = {
            "flow_name": flow_name,
        }
        query_params = {}
        if region:
            query_params["region"] = region
        try:
            # List all secrets
            api_response = api_instance.list_secrets(
                path_params=path_params,  # type: ignore
                query_params=query_params,  # type: ignore
            )
            unnested = util.map_nested_dicts(api_response.body)
            table = []
            for key, value in unnested.items():
                row = []
                row.append(key)
                row.append(value["destination"])
                row.append(value["hash"])
                row.append(
                    datetime.datetime.fromtimestamp(
                        float(value["timestamp"]) / 1000000000.0
                    )
                )
                table.append(row)
                print(
                    tabulate.tabulate(
                        table, headers=("secret", "destination", "hash", "timestamp")
                    )
                )
        except seaplane_framework.api.ApiException as e:
            click.echo(
                click.style(
                    "Exception when calling FlowApi->list_secrets: %s\n" % e, fg="red"
                )
            )


@flow.command(name="set-secret")
@click.argument("flow_name")
@click.argument("secret_name")
@click.option(
    "--destination",
    default="all",
    help="destination for secret (all|carrier-io|processor)",
    type=click.Choice(("all", "carrier-io", "processor")),
)
@click.option("--region")
def set_secret(flow_name, secret_name, destination, region):
    """set or create secret value for a flow"""
    configuration = util.api_config()
    if not configuration:
        return
    with seaplane_framework.api.ApiClient(configuration) as api_client:
        api_instance = flow_api.FlowApi(api_client)
        path_params = {
            "flow_name": flow_name,
            "secret_name": secret_name,
        }
        query_params = {}
        if region:
            query_params["region"] = region
        value = click.prompt("Value for {}".format(secret_name), hide_input=True)
        body = {"destination": destination, "value": value}
        try:
            # Set the secret value
            api_response = api_instance.set_secret(
                path_params=path_params,  # type: ignore
                query_params=query_params,  # type: ignore
                body=body,  # type: ignore
            )
        except seaplane_framework.api.ApiException as e:
            click.echo(
                click.style(
                    "Exception when calling FlowApi->set_secret: %s\n" % e, fg="red"
                )
            )


@flow.command(name="delete-secret")
@click.argument("flow_name")
@click.argument("secret_name")
@click.option("--region")
def delete_secret(flow_name, secret_name, region):
    """delete a flow secret"""
    configuration = util.api_config()
    if not configuration:
        return
    with seaplane_framework.api.ApiClient(configuration) as api_client:
        api_instance = flow_api.FlowApi(api_client)
        path_params = {
            "flow_name": flow_name,
            "secret_name": secret_name,
        }
        query_params = {}
        if region:
            query_params["region"] = region
        try:
            # Set the secret value
            api_response = api_instance.delete_secret(
                path_params=path_params,  # type: ignore
                query_params=query_params,  # type: ignore
            )
        except seaplane_framework.api.ApiException as e:
            click.echo(
                click.style(
                    "Exception when calling FlowApi->delete_secret: %s\n" % e, fg="red"
                )
            )
