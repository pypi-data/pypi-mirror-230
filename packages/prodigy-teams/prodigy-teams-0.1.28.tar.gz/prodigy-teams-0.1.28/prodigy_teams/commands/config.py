from radicli import Arg
from wasabi import msg

from .. import ty
from ..cli import cli
from ..config import global_config_dir
from ..messages import Messages
from ..query import resolve_action_id, resolve_project_id, resolve_task_id
from ..util import URL
from ._state import get_root_cfg, get_saved_settings


@cli.subcommand("config", "reset")
def reset() -> None:
    """Reset all caching and configuration."""
    queue = list(global_config_dir().iterdir())
    for subpath in queue:
        if subpath.is_dir():
            queue.extend(list(subpath.iterdir()))
        else:
            msg.info(Messages.T021.format(subpath=subpath))
            subpath.unlink()


@cli.subcommand(
    "config",
    "project",
    name_or_id=Arg(help=Messages.name_or_id.format(noun="project")),
)
def project(name_or_id: ty.StrOrUUID) -> ty.UUID:
    """Set the default project."""
    root_cfg = get_root_cfg()
    project_id = resolve_project_id(name_or_id)
    settings = get_saved_settings()
    settings.update("project", project_id)
    settings.save(root_cfg.saved_settings_path)
    msg.good(Messages.T019.format(noun="project", name=project_id))
    return project_id


@cli.subcommand(
    "config",
    "task",
    name_or_id=Arg(help=Messages.name_or_id.format(noun="task")),
    project_id=Arg(help=Messages.project_id.format(noun="task")),
    cluster_id=Arg(help=Messages.cluster_id.format(noun="task")),
)
def task(
    name_or_id: ty.StrOrUUID,
    cluster_id: ty.Optional[ty.UUID] = None,
    project_id: ty.Optional[ty.UUID] = None,
) -> ty.UUID:
    """Set the default task."""
    root_cfg = get_root_cfg()
    task_id = resolve_task_id(name_or_id, project_id=project_id, broker_id=cluster_id)
    settings = get_saved_settings()
    settings.update("task", task_id)
    settings.save(root_cfg.saved_settings_path)
    msg.good(Messages.T019.format(noun="task", name=task_id))
    return task_id


@cli.subcommand(
    "config",
    "action",
    name_or_id=Arg(help=Messages.name_or_id.format(noun="action")),
    project_id=Arg(help=Messages.project_id.format(noun="action")),
    cluster_id=Arg(help=Messages.cluster_id.format(noun="action")),
)
def action(
    name_or_id: ty.StrOrUUID,
    cluster_id: ty.Optional[ty.UUID] = None,
    project_id: ty.Optional[ty.UUID] = None,
) -> ty.UUID:
    """Set the default action."""
    root_cfg = get_root_cfg()
    action_id = resolve_action_id(
        name_or_id, project_id=project_id, broker_id=cluster_id
    )
    settings = get_saved_settings()
    settings.update("action", action_id)
    settings.save(root_cfg.saved_settings_path)

    msg.good(Messages.T019.format(noun="action", name=action_id))
    return action_id


@cli.subcommand(
    "config",
    "set-cluster-host",
    host=Arg(help=Messages.cluster_host_config),
)
def set_broker_host(host: str) -> None:
    """Set the broker cluster host."""
    root_cfg = get_root_cfg()
    host_url = URL.parse(host)
    settings = get_saved_settings()
    settings.update("broker_host", str(host_url))
    settings.save(root_cfg.saved_settings_path)
    msg.good(Messages.T019.format(noun="cluster host", name=host))


@cli.subcommand(
    "config",
    "set-pam-host",
    host=Arg(help=Messages.pam_host_config),
)
def set_pam_host(host: str) -> None:
    """Set the PAM host."""
    root_cfg = get_root_cfg()
    host_url = URL.parse(host)
    settings = get_saved_settings()
    settings.update("pam_host", str(host_url))
    settings.save(root_cfg.saved_settings_path)
    msg.good(Messages.T019.format(noun="PAM host", name=host))
