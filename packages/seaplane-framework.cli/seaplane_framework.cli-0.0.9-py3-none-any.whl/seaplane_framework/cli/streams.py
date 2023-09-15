import pprint

import click
import yaml

import seaplane_framework.api
from seaplane_framework.api.apis.tags import stream_api
from seaplane_framework.cli import util


@click.group()
def stream():
    """Seaplane Streams"""


@stream.command()
@click.argument("stream_name")
@click.option(
    "--stream-options", help="Stream options JSON/YAML, @ to load a file, @- for stdin"
)
def create(stream_name, stream_options):
    """create a stream"""
    configuration = util.api_config()
    if not configuration:
        return
    options = {}
    if stream_options:
        options = yaml.safe_load(util.read_or_return_string(stream_options))
    with seaplane_framework.api.ApiClient(configuration) as api_client:
        api_instance = stream_api.StreamApi(api_client)
        path_params = {
            "stream_name": stream_name,
        }
        try:
            resp = api_instance.create_stream(
                path_params=path_params,  # type: ignore
                body=options,  # type: ignore
            )
            click.echo(click.style("Created", fg="green"))
        except seaplane_framework.api.ApiException as e:
            click.echo(
                click.style(
                    "Exception when calling StreamApi->create_stream: %s\n" % e,
                    fg="red",
                )
            )


@stream.command()
def list():
    """list all streams"""
    configuration = util.api_config()
    if not configuration:
        return
    with seaplane_framework.api.ApiClient(configuration) as api_client:
        api_instance = stream_api.StreamApi(api_client)
        try:
            resp = api_instance.list_streams()
            for stream in resp.body:
                print(stream)
        except seaplane_framework.api.ApiException as e:
            click.echo(
                click.style(
                    "Exception when calling StreamApi->list_streams: %s\n" % e, fg="red"
                )
            )


@stream.command()
@click.argument("stream_name")
def delete(stream_name):
    """delete a stream"""
    configuration = util.api_config()
    if not configuration:
        return
    with seaplane_framework.api.ApiClient(configuration) as api_client:
        api_instance = stream_api.StreamApi(api_client)
        path_params = {
            "stream_name": stream_name,
        }
        try:
            resp = api_instance.delete_stream(path_params=path_params)  # type: ignore
            click.echo(click.style("Deleted", fg="green"))
        except seaplane_framework.api.ApiException as e:
            click.echo(
                click.style(
                    "Exception when calling StreamApi->delete_stream: %s\n" % e,
                    fg="red",
                )
            )


@stream.command()
@click.argument("stream_name")
def details(stream_name):
    """show details (configuration) for a stream"""
    configuration = util.api_config()
    if not configuration:
        return
    with seaplane_framework.api.ApiClient(configuration) as api_client:
        api_instance = stream_api.StreamApi(api_client)
        path_params = {
            "stream_name": stream_name,
        }
        try:
            resp = api_instance.get_stream(path_params=path_params)
            pprint.pprint(util.map_nested_dicts(resp.body))
        except seaplane_framework.api.ApiException as e:
            click.echo(
                click.style(
                    "Exception when calling StreamApi->list_streams: %s\n" % e, fg="red"
                )
            )
