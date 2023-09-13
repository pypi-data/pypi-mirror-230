import builtins

from radicli import Arg
from wasabi import msg

from .. import ty
from ..cli import cli
from ..errors import CLIError, ProdigyTeamsErrors
from ..messages import Messages
from ..prodigy_teams_pam_sdk.models import BrokerPathDetail, BrokerPathSummary
from ..query import resolve_path, resolve_path_id
from ..ui import print_info_table, print_table_with_select
from ..util import resolve_remote_path
from ._state import get_auth_state


@cli.subcommand(
    "paths",
    "list",
    select=Arg(
        "--select", help=Messages.select.format(opts=list(BrokerPathSummary.__fields__))
    ),
    as_json=Arg("--json", help=Messages.as_json),
)
def list(
    select: ty.List[str] = ["created", "id", "name", "path"], as_json: bool = False
) -> ty.Sequence[BrokerPathSummary]:
    """List all cluster path aliases"""
    client = get_auth_state().client
    res = client.broker_path.all()
    print_table_with_select(res.items, select=select, as_json=as_json)
    return res.items


@cli.subcommand(
    "paths",
    "info",
    name_or_id=Arg(help=Messages.name_or_id.format(noun="path")),
    cluster_id=Arg(help=Messages.cluster_id.format(noun="path")),
    select=Arg(
        "--select",
        help=Messages.select.format(opts=builtins.list(BrokerPathDetail.__fields__)),
    ),
    as_json=Arg("--json", help=Messages.as_json),
)
def info(
    name_or_id: ty.StrOrUUID,
    cluster_id: ty.Optional[ty.UUID] = None,
    select: ty.Optional[ty.List[str]] = None,
    as_json: bool = False,
) -> BrokerPathDetail:
    """Get detailed info for a path alias"""
    res = resolve_path(name_or_id, broker_id=cluster_id)
    print_info_table(res, as_json=as_json, select=select)
    return res


@cli.subcommand(
    "paths",
    "create",
    name=Arg(help=Messages.name.format(noun="path")),
    path=Arg(help=Messages.path.format(noun="cluster directory")),
    exists_ok=Arg("--exists-ok", help=Messages.exists_ok),
)
def create(name: str, path: str, exists_ok: bool = False) -> ty.Optional[ty.UUID]:
    """Create a new path alias"""
    auth = get_auth_state()
    client = auth.client
    broker_id = auth.broker_id
    path = resolve_remote_path(client, path, default_broker=auth.broker_host)
    try:
        res = client.broker_path.create(name=name, path=path, broker_id=broker_id)
    except ProdigyTeamsErrors.BrokerPathExists:
        if exists_ok:
            msg.info(Messages.T001.format(noun="path", name=name))
            return None
        raise CLIError(Messages.E002.format(noun="path", name=name))
    except ProdigyTeamsErrors.BrokerPathInvalid:
        raise CLIError(Messages.E004.format(noun="path", name=name))
    except ProdigyTeamsErrors.BrokerPathForbiddenCreate:
        raise CLIError(Messages.E003.format(noun="path", name=name))
    msg.divider("Path Alias")
    msg.table(res.dict())
    return res.id


@cli.subcommand(
    "paths",
    "delete",
    name_or_id=Arg(help=Messages.name_or_id.format(noun="path")),
    cluster_id=Arg(help=Messages.cluster_id.format(noun="path")),
)
def delete(
    name_or_id: ty.StrOrUUID, cluster_id: ty.Optional[ty.UUID] = None
) -> ty.UUID:
    """Delete a path alias"""
    path_id = resolve_path_id(name_or_id, broker_id=cluster_id)
    auth = get_auth_state()
    try:
        auth.client.broker_path.delete(id=path_id)
    except (
        ProdigyTeamsErrors.ProjectForbiddenDelete,
        ProdigyTeamsErrors.ProjectNotFound,
    ):
        raise CLIError(Messages.E006.format(noun="path", name=name_or_id))
    else:
        msg.good(Messages.T003.format(noun="path", name=name_or_id))
    return path_id
