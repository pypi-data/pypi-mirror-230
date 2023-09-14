import builtins

from radicli import Arg
from wasabi import msg

from .. import ty
from ..cli import cli
from ..errors import CLIError, ProdigyTeamsErrors
from ..messages import Messages
from ..prodigy_teams_pam_sdk.models import PackageDetail, PackageSummary
from ..query import resolve_package
from ..ui import print_info_table, print_table_with_select
from ._state import get_auth_state


@cli.subcommand(
    "packages",
    "list",
    # fmt: off
    select=Arg("--select", help=Messages.select.format(opts=list(PackageSummary.__fields__))),
    as_json=Arg("--json", help=Messages.as_json),
    # fmt: on
)
def list(
    select: ty.List[str] = ["id", "name", "version", "recipe_count", "num_used_by"],
    as_json: bool = False,
) -> ty.Sequence[PackageSummary]:
    """List all packages"""
    client = get_auth_state().client
    res = client.package.all_readable()

    print_table_with_select(res.items, select=select, as_json=as_json)

    return res.items


@cli.subcommand(
    "packages",
    "info",
    name_or_id=Arg(help=Messages.name_or_id.format(noun="package")),
    cluster_id=Arg(help=Messages.cluster_id.format(noun="package")),
    select=Arg(
        "--select",
        help=Messages.select.format(opts=builtins.list(PackageDetail.__fields__)),
    ),
    as_json=Arg("--json", help=Messages.as_json),
)
def info(
    name_or_id: ty.StrOrUUID,
    cluster_id: ty.Optional[ty.UUID] = None,
    select: ty.Optional[ty.List[str]] = None,
    as_json: bool = False,
) -> PackageDetail:
    """Get detailed info for a package"""
    auth = get_auth_state()
    if cluster_id is None:
        cluster_id = auth.broker_id
    res = resolve_package(name_or_id, broker_id=cluster_id)
    print_info_table(
        res, exclude=["tasks", "actions", "meta"], as_json=as_json, select=select
    )
    return res


@cli.subcommand(
    "packages",
    "create",
    name=Arg(help=Messages.name.format(noun="package")),
    kind=Arg("--kind", help=Messages.kind.format(noun="package")),
    exists_ok=Arg("--exists-ok", help=Messages.exists_ok),
)
def create(name: str, kind: str, exists_ok: bool = False) -> ty.Optional[ty.UUID]:
    """Create a new package"""
    auth = get_auth_state()
    client = auth.client
    broker_id = auth.broker_id
    try:
        res = client.package.create(name=name, kind=kind, broker_id=broker_id)
    except ProdigyTeamsErrors.PackageExists:
        if exists_ok:
            msg.info(Messages.T001.format(noun="package", name=name))
            return None
        raise CLIError(Messages.E002.format(noun="package", name=name))
    except ProdigyTeamsErrors.PackageInvalid:
        raise CLIError(Messages.E004.format(noun="package", name=name))
    except ProdigyTeamsErrors.PackageForbiddenCreate:
        raise CLIError(Messages.E003.format(noun="package", name=name))
    msg.divider("Package")
    msg.table(res.dict())
    return res.id


@cli.subcommand(
    "packages",
    "delete",
    name_or_id=Arg(help=Messages.name_or_id.format(noun="package")),
    cluster_id=Arg(help=Messages.cluster_id.format(noun="package")),
    force=Arg("--force", help="Delete related actions or tasks as well"),
)
def delete(
    name_or_id: ty.StrOrUUID,
    cluster_id: ty.Optional[ty.UUID] = None,
    force: bool = False,
) -> ty.UUID:
    """Delete a package"""
    auth = get_auth_state()
    if cluster_id is None:
        cluster_id = auth.broker_id
    package = resolve_package(name_or_id, broker_id=cluster_id)
    package_id = package.id
    try:
        auth.client.package.delete(id=package_id, force=force)
    except ProdigyTeamsErrors.PackageForbiddenDeleteForExistingPlans:
        raise CLIError(
            Messages.E048.format(
                noun="package",
                name=name_or_id,
                others="other actions or tasks",
                flag="--force",
            )
        )
    except (
        ProdigyTeamsErrors.PackageForbiddenDelete,
        ProdigyTeamsErrors.PackageNotFound,
    ):
        raise CLIError(Messages.E006.format(noun="package", name=name_or_id))
    else:
        msg.good(Messages.T003.format(noun="package", name=name_or_id))
    return package_id
