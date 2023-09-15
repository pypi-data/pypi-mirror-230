import sys

import click
import tabulate
import yaml

import seaplane_framework.api
from seaplane_framework.api.apis.tags import key_value_api
from seaplane_framework.cli import util
from seaplane_framework.api.model import key_value_etag


@click.group()
def kv():
    """Seaplane KV Store"""


@kv.command(name="list-stores")
def list_stores():
    """list stores"""
    configuration = util.api_config()
    if not configuration:
        return
    with seaplane_framework.api.ApiClient(configuration) as api_client:
        api_instance = key_value_api.KeyValueApi(api_client)
        try:
            resp = api_instance.list_stores()
            table = []
            for name in sorted(resp.body):
                table.append((name,))
            print(tabulate.tabulate(table, headers=("name",)))
        except seaplane_framework.api.ApiException as e:
            click.echo(
                click.style(
                    "Exception when calling KeyValueApi->get_stores: %s\n" % e.reason,
                    fg="red",
                )
            )


@kv.command(name="create-store")
@click.argument("store_name")
@click.option(
    "--store-options", help="Store options JSON/YAML, @ to load a file, @- for stdin"
)
def create_store(store_name, store_options):
    """create a KV store"""
    configuration = util.api_config()
    if not configuration:
        return
    options = {}
    if store_options:
        options = yaml.safe_load(util.read_or_return_string(store_options))
    with seaplane_framework.api.ApiClient(configuration) as api_client:
        api_instance = key_value_api.KeyValueApi(api_client)
        path_params = {
            "kv_store": store_name,
        }
        try:
            resp = api_instance.create_store(
                path_params=path_params,  # type: ignore
                body=options,  # type: ignore
            )
            click.echo(click.style("Created {}".format(store_name), fg="green"))
        except seaplane_framework.api.ApiException as e:
            click.echo(
                click.style(
                    "Exception when calling KeyValueApi->create_store: %s\n" % e.reason,
                    fg="red",
                )
            )


@kv.command(name="delete-store")
@click.argument("store_name")
@click.confirmation_option(prompt="Are you sure you want to delete store?")
def delete_store(store_name):
    """delete a KV store"""
    configuration = util.api_config()
    if not configuration:
        return
    options = {}
    with seaplane_framework.api.ApiClient(configuration) as api_client:
        api_instance = key_value_api.KeyValueApi(api_client)
        path_params = {
            "kv_store": store_name,
        }
        try:
            resp = api_instance.delete_store(
                path_params=path_params,  # type: ignore
            )
            click.echo(click.style("Deleted {}".format(store_name), fg="green"))
        except seaplane_framework.api.ApiException as e:
            click.echo(
                click.style(
                    "Exception when calling KeyValueApi->delete_store: %s\n" % e.reason,
                    fg="red",
                )
            )


@kv.command(name="set")
@click.argument("store_name")
@click.argument("key")
@click.argument("value")
@click.option(
    "--version-id",
    help="Unique version ID, succeed only if it matches the current version ID",
)
@click.option(
    "--create-exclusive/--no-create-exclusive",
    help="Create only if it does not exist",
    type=bool,
    default=False,
)
def set_key(store_name, key, value, version_id, create_exclusive):
    """set a key value"""
    configuration = util.api_config()
    if not configuration:
        return
    path_params = {
        "kv_store": store_name,
        "key": key,
    }
    header_params = {}
    if create_exclusive and version_id is not None:
        raise click.UsageError(
            "--create-exclusive and --version cannot be used at the same time"
        )
    if create_exclusive:
        header_params = {"If-Not-Match": "*"}
    if version_id is not None:
        header_params = {"If-Match": key_value_etag.KeyValueEtag(version_id)}
    with seaplane_framework.api.ApiClient(configuration) as api_client:
        api_instance = key_value_api.KeyValueApi(api_client)
        try:
            resp = api_instance.put_key(
                path_params=path_params,  # type: ignore
                header_params=header_params,  # type: ignore
                body=util.read_or_return_string(value).encode("utf-8"),  # type: ignore
            )
        except seaplane_framework.api.ApiException as e:
            if e.status == 412:
                if version_id is None:
                    print("key already exists")
                else:
                    print("version ID ({}) does not match".format(version_id))
            else:
                print("Exception when calling KeyValueApi->put_key: %s\n" % e)


@kv.command(name="get")
@click.argument("store_name")
@click.argument("key")
@click.option(
    "--version-id",
    help="Unique version ID, succeed only if it matches the current revision",
)
def get_key(store_name, key, version_id):
    """set a key value"""
    configuration = util.api_config()
    if not configuration:
        return
    path_params = {
        "kv_store": store_name,
        "key": key,
    }
    header_params = (
        {}
        if version_id is None
        else {"If-Match": key_value_etag.KeyValueEtag(version_id)}
    )
    with seaplane_framework.api.ApiClient(configuration) as api_client:
        api_instance = key_value_api.KeyValueApi(api_client)
        try:
            resp = api_instance.get_key(
                path_params=path_params,  # type: ignore
                header_params=header_params,  # type: ignore
                stream=True,
                accept_content_types=("application/octet-stream",),
                timeout=300,
                skip_deserialization=True,
            )
            print(resp.response.read())
            print("revision: {}".format(resp.response.headers["ETag"]), file=sys.stderr)
        except seaplane_framework.api.ApiException as e:
            if e.status == 412:
                print("version ({}) does not match".format(version_id))
            else:
                print("Exception when calling KeyValueApi->get_key: %s\n" % e)


@kv.command(name="del")
@click.argument("store_name")
@click.argument("key")
@click.option(
    "--version-id",
    help="Unique version ID, succeed only if it matches the current revision",
)
@click.option(
    "--purge/--no-purge", help="Purge the key completely", type=bool, default=False
)
def del_key(store_name, key, version_id, purge):
    """set a key value"""
    configuration = util.api_config()
    if not configuration:
        return
    path_params = {
        "kv_store": store_name,
        "key": key,
    }
    header_params = (
        {}
        if version_id is None
        else {"If-Match": key_value_etag.KeyValueEtag(version_id)}
    )
    with seaplane_framework.api.ApiClient(configuration) as api_client:
        api_instance = key_value_api.KeyValueApi(api_client)
        try:
            resp = api_instance.delete_key(
                path_params=path_params,  # type: ignore
                header_params=header_params,  # type: ignore
                query_params={"purge": "true" if purge else "false"},  # type: ignore
            )
            click.echo(click.style("Deleted {}".format(key), fg="green"))
        except seaplane_framework.api.ApiException as e:
            if e.status == 412:
                print("version ({}) does not match".format(version_id))
            else:
                print("Exception when calling KeyValueApi->del_key: %s\n" % e)
