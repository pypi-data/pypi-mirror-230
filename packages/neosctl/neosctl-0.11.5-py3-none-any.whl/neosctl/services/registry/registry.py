import typing

import httpx
import typer

from neosctl import constant, util
from neosctl.services.registry.schema import MigrateCore, RegisterCore, RemoveCore
from neosctl.util import process_response

app = typer.Typer()


ACCOUNT_ARG = typer.Option(None, help="Account override (root only).", callback=util.sanitize)


def _core_url(registry_api_url: str) -> str:
    return "{}/core".format(registry_api_url.rstrip("/"))


def _data_product_url(registry_api_url: str, postfix: str = "") -> str:
    return "{}/data_product{}".format(registry_api_url.rstrip("/"), postfix)


@app.command(name="register-core")
def register_core(
    ctx: typer.Context,
    partition: str = typer.Argument(..., help="Core partition", callback=util.sanitize),
    name: str = typer.Argument(..., help="Core name", callback=util.sanitize),
    account: typing.Optional[str] = ACCOUNT_ARG,
) -> None:
    """Register a core.

    Register a core to receive an identifier and access key for use in deployment.
    """

    @util.ensure_login
    def _request(ctx: typer.Context, rc: RegisterCore) -> httpx.Response:
        return util.post(
            ctx,
            constant.REGISTRY,
            _core_url(ctx.obj.get_registry_api_url()),
            json=rc.model_dump(exclude_none=True),
            headers={"X-Partition": partition},
            account=account,
        )

    rc = RegisterCore(name=name)

    r = _request(ctx, rc)
    process_response(r)


@app.command(name="migrate-core")
def migrate_core(
    ctx: typer.Context,
    identifier: str = typer.Option(..., help="Core identifier"),
    urn: str = typer.Option(..., help="Core urn", callback=util.sanitize),
    account: str = typer.Option(..., help="Account name", callback=util.sanitize),
) -> None:
    """Migrate a core out of root account.

    Migrate a core from `root` into an actual account.
    """

    @util.ensure_login
    def _request(ctx: typer.Context, mc: MigrateCore) -> httpx.Response:
        return util.post(
            ctx,
            constant.REGISTRY,
            f"{_core_url(ctx.obj.get_registry_api_url())}/{identifier}/migrate",
            json=mc.model_dump(),
        )

    mc = MigrateCore(
        urn=urn,
        account=account,
    )

    r = _request(ctx, mc)
    process_response(r)


@app.command(name="list-cores")
def list_cores(
    ctx: typer.Context,
    search: str = typer.Option(None, help="Search core name(s)", callback=util.sanitize),
) -> None:
    """List existing registered cores."""

    @util.ensure_login
    def _request(ctx: typer.Context) -> httpx.Response:
        return util.get(
            ctx,
            constant.REGISTRY,
            _core_url(ctx.obj.get_registry_api_url()),
            params={"search": search} if search else None,
        )

    r = _request(ctx)
    process_response(r)


@app.command(name="remove-core")
def remove_core(
    ctx: typer.Context,
    identifier: str = typer.Option(..., help="Core identifier"),
    urn: str = typer.Option(..., help="Core urn", callback=util.sanitize),
) -> None:
    """Remove a registered core."""

    @util.ensure_login
    def _request(ctx: typer.Context, rc: RemoveCore) -> httpx.Response:
        return util.delete(
            ctx,
            constant.REGISTRY,
            f"{_core_url(ctx.obj.get_registry_api_url())}/{identifier}",
            json=rc.model_dump(exclude_none=True),
        )

    rc = RemoveCore(urn=urn)

    r = _request(ctx, rc)
    process_response(r)


@app.command(name="search")
def search_products(
    ctx: typer.Context,
    search_term: str = typer.Argument(..., callback=util.sanitize),
) -> None:
    """Search published data products across cores."""

    @util.ensure_login
    def _request(ctx: typer.Context, search_term: str) -> httpx.Response:
        return util.get(
            ctx,
            constant.REGISTRY,
            _data_product_url(ctx.obj.get_registry_api_url(), "/search"),
            params={"search_term": search_term},
        )

    r = _request(ctx, search_term)
    process_response(r)


@app.command(name="get-product")
def get_product(
    ctx: typer.Context,
    urn: str = typer.Argument(..., callback=util.sanitize),
) -> None:
    """Get data product details."""

    @util.ensure_login
    def _request(ctx: typer.Context, urn: str) -> httpx.Response:
        return util.get(
            ctx,
            constant.REGISTRY,
            _data_product_url(ctx.obj.get_registry_api_url(), f"/urn/{urn}"),
        )

    r = _request(ctx, urn)
    process_response(r)
