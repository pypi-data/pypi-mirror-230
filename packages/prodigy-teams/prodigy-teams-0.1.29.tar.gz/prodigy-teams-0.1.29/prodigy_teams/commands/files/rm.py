from radicli import Arg

from ... import errors, ty
from ...cli import cli
from ...messages import Messages
from ...prodigy_teams_broker_sdk import errors as broker_errors
from ...prodigy_teams_broker_sdk import models as broker_models
from ...ui import msg
from ...util import _resolve_broker_ref, resolve_remote_path
from .._state import get_auth_state, get_saved_settings


@cli.subcommand(
    "files",
    "rm",
    remote_path=Arg(help=Messages.remote_path),
    cluster_host=Arg("--cluster-host", help=Messages.cluster_host),
    missing_ok=Arg("--missing-ok", help=Messages.missing_ok),
    recurse=Arg("--recurse", "-r", help=Messages.recurse_delete),
)
def rm(
    remote_path: str,
    cluster_host: ty.Optional[str] = None,
    missing_ok: bool = False,
    recurse: bool = False,
) -> None:
    """Remove files from the cluster"""
    settings = get_saved_settings()
    auth = get_auth_state()
    broker_host = str(
        _resolve_broker_ref(auth.client, cluster_host or settings.broker_host)
    )
    auth = get_auth_state()
    path = resolve_remote_path(auth.client, remote_path, broker_host)

    body = broker_models.Deleting(path=path, missing_ok=missing_ok, recurse=recurse)
    try:
        auth.broker_client.files.delete(body)
    except broker_errors.RmPathIsADirectoryError as e:
        raise errors.CLIError(Messages.E053.format(name=remote_path)) from e
    except broker_errors.RmPathNotFoundError as e:
        raise errors.CLIError(
            Messages.E006.format(noun="path", name=remote_path)
        ) from e

    msg.info(f"Successfully deleted {path}")
