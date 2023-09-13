import click
import jwt
import requests
import tabulate

import seaplane_framework.config


@click.group()
def auth():
    """Seaplane Auth (JWTs/Keys)"""


@auth.command()
def refresh():
    """refresh JWT"""
    config = seaplane_framework.config.read()
    identity_url = (
        config.current_context.api_key.issuer_url
        or seaplane_framework.config.DEFAULT_KEY_ISSUER_URL
    )
    key = config.current_context.api_key.value
    token = "Bearer {}".format(key)
    resp = requests.request(
        "POST", identity_url, data=None, headers={"Authorization": token}
    )
    if resp.status_code == 200:
        click.echo(click.style("JWT refreshed", fg="green"))
    else:
        click.echo(
            click.style("Error {}:".format(resp.status_code), fg="red")
            + str(resp.content)
        )
    jwt = resp.content.decode()
    config.current_context.options["jwt"] = jwt.strip()
    seaplane_framework.config.write(config)


@auth.command()
def details():
    """show details about the current JWT (if any)"""
    config = seaplane_framework.config.read()
    seaplane_jwt = config.current_context.options.get("jwt")
    if not seaplane_jwt:
        click.echo(
            click.style("Error: ", fg="red")
            + "no JWT for this context (try auth refresh)"
        )
        return
    decoded = jwt.decode(jwt=seaplane_jwt, options={"verify_signature": False})
    click.echo(tabulate.tabulate(decoded.items(), headers=("claim", "value")))


@auth.command(name="jwt")
def jwt_dump():
    """echo the current JWT"""
    config = seaplane_framework.config.read()
    seaplane_jwt = config.current_context.options.get("jwt")
    print(seaplane_jwt)
