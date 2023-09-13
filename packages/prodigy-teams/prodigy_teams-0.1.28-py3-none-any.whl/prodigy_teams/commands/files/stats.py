from radicli import Arg

from ... import ty
from ...cli import cli
from ...messages import Messages
from ...prodigy_teams_broker_sdk import models as broker_models
from ...ui import print_as_json, print_table_with_select
from ...util import _resolve_broker_ref, resolve_remote_path
from .._state import get_auth_state, get_saved_settings


@cli.subcommand(
    "files",
    "stats",
    remote_path=Arg(help=Messages.remote_path),
    cluster_host=Arg("--cluster-host", help=Messages.cluster_host),
    as_json=Arg("--json", help=Messages.as_json),
)
def stat(
    remote_path: str, cluster_host: ty.Optional[str] = None, as_json: bool = False
) -> broker_models.FileStats:
    """Get the stats for a file located in `remote_path`"""
    settings = get_saved_settings()
    auth = get_auth_state()
    broker_host = str(
        _resolve_broker_ref(auth.client, cluster_host or settings.broker_host)
    )
    assert broker_host is not None
    auth = get_auth_state()
    path = resolve_remote_path(auth.client, remote_path, broker_host)
    # We don't necessarily want to exit here if it's not found? How else should
    # a script check whether the file exists?
    body = broker_models.Statting(path=path)
    stats = auth.broker_client.files.stat(body)
    if as_json:
        print_as_json(stats.dict())
    else:
        # TODO: Fix output
        print_table_with_select([stats], select=["modification_time", "size"])
    return stats
