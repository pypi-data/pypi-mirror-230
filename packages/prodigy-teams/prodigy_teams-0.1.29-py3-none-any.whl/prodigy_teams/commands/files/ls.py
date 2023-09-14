from radicli import Arg
from wasabi import msg

from ... import ty
from ...cli import cli
from ...messages import Messages
from ...prodigy_teams_broker_sdk import models as broker_models
from ...ui import print_as_json
from ...util import _resolve_broker_ref, resolve_remote_path
from .._state import get_auth_state, get_saved_settings


@cli.subcommand(
    "files",
    "ls",
    remote=Arg(help=Messages.remote_path),
    recurse=Arg("--recurse", "-r", help=Messages.recurse_list),
    as_json=Arg("--json", help=Messages.as_json),
    cluster_host=Arg("--cluster-host", help=Messages.cluster_host),
)
def ls(
    remote: str,
    recurse: bool = False,
    as_json: bool = False,
    cluster_host: ty.Optional[str] = None,
) -> broker_models.PathList:
    """List the files under `remote`"""
    settings = get_saved_settings()
    auth = get_auth_state()
    broker_host = _resolve_broker_ref(auth.client, cluster_host or settings.broker_host)
    path = resolve_remote_path(auth.client, remote, str(broker_host))
    body = broker_models.Listing(path=path, recurse=recurse, include_stats=False)
    files = auth.broker_client.files.list_dir(body)
    if as_json:
        print_as_json(files.dict())
    else:
        msg.info(remote)
        for file_path in files.paths:
            print(file_path)
    return files
