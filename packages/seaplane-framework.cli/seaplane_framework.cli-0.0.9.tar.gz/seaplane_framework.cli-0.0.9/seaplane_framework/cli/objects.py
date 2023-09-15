import datetime

import click
import tabulate
import yaml

import seaplane_framework.api
from seaplane_framework.api.apis.tags import object_api
from seaplane_framework.cli import util


@click.group(name="object")
def object_group():
    """Seaplane Object Store"""


@object_group.command(name="create-bucket")
@click.argument("bucket_name")
@click.option(
    "--bucket-options", help="Bucket options JSON/YAML, @ to load a file, @- for stdin"
)
def create_bucket(bucket_name, bucket_options):
    """create a bucket"""
    configuration = util.api_config()
    if not configuration:
        return
    options = {}
    if bucket_options:
        options = yaml.safe_load(util.read_or_return_string(bucket_options))
    with seaplane_framework.api.ApiClient(configuration) as api_client:
        api_instance = object_api.ObjectApi(api_client)
        path_params = {
            "bucket_name": bucket_name,
        }
        try:
            resp = api_instance.create_bucket(
                path_params=path_params,  # type: ignore
                body=options,  # type: ignore
            )
            click.echo(click.style("Created {}".format(bucket_name), fg="green"))
        except seaplane_framework.api.ApiException as e:
            click.echo(
                click.style(
                    "Exception when calling ObjectApi->create_bucket: %s\n" % e.reason,
                    fg="red",
                )
            )


@object_group.command(name="list-buckets")
def list_buckets():
    """list buckets"""
    configuration = util.api_config()
    if not configuration:
        return
    with seaplane_framework.api.ApiClient(configuration) as api_client:
        api_instance = object_api.ObjectApi(api_client)
        try:
            resp = api_instance.list_buckets()  # type: ignore
            table = []
            for name, details in sorted(resp.body.items()):
                print(name, details)
                table.append(
                    (
                        name,
                        details.get("replicas", 3),
                        details.get("description", ""),
                        details.get("notify", ""),
                    )
                )
            print(
                tabulate.tabulate(
                    table, headers=("name", "replicas", "description", "notify")
                )
            )
        except seaplane_framework.api.ApiException as e:
            click.echo(
                click.style(
                    "Exception when calling ObjectApi->list_buckets: %s\n" % e.reason,
                    fg="red",
                )
            )


@object_group.command(name="delete-bucket")
@click.argument("bucket_name")
@click.confirmation_option(prompt="Are you sure you want to delete bucket?")
def delete_bucket(bucket_name):
    """delete a bucket"""
    configuration = util.api_config()
    if not configuration:
        return
    with seaplane_framework.api.ApiClient(configuration) as api_client:
        api_instance = object_api.ObjectApi(api_client)
        path_params = {
            "bucket_name": bucket_name,
        }
        try:
            resp = api_instance.delete_bucket(path_params=path_params)  # type: ignore
            click.echo(click.style("Deleted {}".format(bucket_name), fg="green"))
        except seaplane_framework.api.ApiException as e:
            click.echo(
                click.style(
                    "Exception when calling ObjectApi->delete_bucket: %s\n" % e.reason,
                    fg="red",
                )
            )


@object_group.command(name="upload")
@click.argument("bucket_name")
@click.argument("source", type=click.File("rb"))
@click.argument("destination")
def upload(bucket_name, source, destination):
    """upload an object to a bucket"""
    configuration = util.api_config()
    if not configuration:
        return
    with seaplane_framework.api.ApiClient(configuration) as api_client:
        api_instance = object_api.ObjectApi(api_client)
        path_params = {
            "bucket_name": bucket_name,
        }
        query_params = {
            "path": destination,
        }
        try:
            api_response = api_instance.create_object(
                path_params=path_params,  # type: ignore
                query_params=query_params,  # type: ignore
                body=source,  # type: ignore
            )
        except seaplane_framework.api.ApiException as e:
            click.echo(
                click.style(
                    "Exception when calling ObjectApi->create_object: %s\n" % e.reason,
                    fg="red",
                )
            )


@object_group.command(name="download")
@click.argument("bucket_name")
@click.argument("source")
@click.argument(
    "destination", type=click.Path(exists=False, file_okay=True, writable=True)
)
def download(bucket_name, source, destination):
    """download an object from a bucket"""
    configuration = util.api_config()
    if not configuration:
        return
    with seaplane_framework.api.ApiClient(configuration) as api_client:
        api_instance = object_api.ObjectApi(api_client)
        path_params = {
            "bucket_name": bucket_name,
        }
        query_params = {
            "path": source,
        }
        try:
            # Get an object in a bucket
            api_response = api_instance.get_object(
                path_params=path_params,  # type: ignore
                query_params=query_params,  # type: ignore
                stream=True,
                accept_content_types=("application/octet-stream",),
                timeout=300,
                skip_deserialization=True,
            )
            length = int(api_response.response.headers["content-length"])
            with open(destination, "wb") as destination_file:
                with click.progressbar(length=length, label="Downloading") as bar:
                    for chunk in api_response.response.stream(2**16):
                        destination_file.write(chunk)
                        bar.update(len(chunk))
        except seaplane_framework.api.ApiException as e:
            click.echo(
                click.style(
                    "Exception when calling ObjectApi->get_object: %s\n" % e.reason,
                    fg="red",
                )
            )


@object_group.command(name="delete")
@click.argument("bucket_name")
@click.argument("object_name")
def delete(bucket_name, object_name):
    """delete an object from a bucket"""
    configuration = util.api_config()
    if not configuration:
        return
    with seaplane_framework.api.ApiClient(configuration) as api_client:
        api_instance = object_api.ObjectApi(api_client)
        path_params = {
            "bucket_name": bucket_name,
        }
        query_params = {
            "path": object_name,
        }
        try:
            # Delete an object in a bucket
            api_response = api_instance.delete_object(
                path_params=path_params,  # type: ignore
                query_params=query_params,  # type: ignore
            )
        except seaplane_framework.api.ApiException as e:
            click.echo(
                click.style(
                    "Exception when calling ObjectApi->delete_object: %s\n" % e.reason,
                    fg="red",
                )
            )


@object_group.command(name="list")
@click.argument("bucket_name")
@click.argument("prefix")
def list(bucket_name, prefix):
    """list all objects in a bucket under a prefix"""
    configuration = util.api_config()
    if not configuration:
        return
    with seaplane_framework.api.ApiClient(configuration) as api_client:
        api_instance = object_api.ObjectApi(api_client)
        path_params = {
            "bucket_name": bucket_name,
        }
        query_params = {
            "path": prefix,
        }
        try:
            # Get an object in a bucket
            api_response = api_instance.list_objects(
                path_params=path_params,  # type: ignore
                query_params=query_params,  # type: ignore
            )
            table = [
                (
                    x["name"],
                    x["digest"],
                    datetime.datetime.fromtimestamp(int(x["mod_time"])),
                    sizeof_fmt(int(x["size"])),
                )
                for x in api_response.body
            ]
            click.echo(
                tabulate.tabulate(table, headers=("name", "digest", "mod_time", "size"))
            )
        except seaplane_framework.api.ApiException as e:
            click.echo(
                click.style(
                    "Exception when calling ObjectApi->list_objects: %s\n" % e.reason,
                    fg="red",
                )
            )


# A little copy paste is better than a little dependency.
def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"
