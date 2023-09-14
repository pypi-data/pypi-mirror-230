from functools import cached_property
from pathlib import Path

from pydantic import BaseModel

from . import ty
from .util import APP_NAME, get_app_dir


def global_config_dir() -> Path:
    return Path(get_app_dir(APP_NAME))


class RootConfig:
    def __init__(self, *, config_dir: Path) -> None:
        self.config_dir = config_dir

    @cached_property
    def secrets_path(self) -> Path:
        return self.config_dir / "secrets.json"

    @cached_property
    def saved_settings_path(self) -> Path:
        return self.config_dir / "saved-defaults.json"


class SavedSettings(BaseModel):
    broker_host: ty.Optional[str]
    project: ty.Optional[ty.UUID]
    task: ty.Optional[ty.UUID]
    action: ty.Optional[ty.UUID]
    pam_host: ty.Optional[str]

    @classmethod
    def blank(cls) -> "SavedSettings":
        return cls(
            broker_host=None, project=None, task=None, action=None, pam_host=None
        )

    @classmethod
    def from_file(cls, path: Path, must_exist: bool = False) -> "SavedSettings":
        try:
            return cls.parse_file(path)
        except FileNotFoundError:
            if not must_exist:
                return cls.blank()
            else:
                raise

    def reset_defaults(self) -> None:
        """Reset defaut project/task/action, e.g. on host changes."""
        self.project = None
        self.task = None
        self.action = None

    def to_json(self) -> ty.JSONableDict:
        data = {}
        for key, value in self.dict().items():
            # UUIDs are not JSON-seriazliable by default
            data[key] = str(value) if isinstance(value, ty.UUID) else value
        return data

    def save(
        self,
        path: Path,
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.json(), encoding="utf-8")

    @ty.overload
    def get(self, field: ty.Literal["broker_host", "pam_host"]) -> str:
        ...

    @ty.overload
    def get(self, field: ty.Literal["project", "task", "action"]) -> str:
        ...

    def get(
        self, field: ty.Literal["broker_host", "pam_host", "project", "task", "action"]
    ) -> ty.Union[str, ty.UUID]:
        return getattr(self, field)

    @ty.overload
    def update(
        self,
        field: ty.Literal["broker_host", "pam_host"],
        value: ty.Optional[str] = None,
    ) -> str:
        ...

    @ty.overload
    def update(
        self,
        field: ty.Literal["project", "task", "action"],
        value: ty.Optional[ty.UUID] = None,
    ) -> ty.UUID:
        ...

    def update(
        self,
        field: ty.Literal["broker_host", "pam_host", "project", "task", "action"],
        value: ty.Optional[ty.Union[str, ty.UUID]] = None,
    ) -> ty.Union[str, ty.UUID]:
        old_value = getattr(self, field)
        setattr(self, field, value)
        if old_value != value and field in ["broker_host", "pam_host"]:
            self.reset_defaults()
        return getattr(self, field)
