from contextlib import ExitStack, contextmanager
from contextvars import ContextVar

from .. import auth, config, ty

ROOT_CONFIG: ContextVar[ty.Optional[config.RootConfig]] = ContextVar(
    "root_config", default=None
)
AUTH_STATE: ContextVar[ty.Optional[auth.AuthState]] = ContextVar(
    "cli_auth", default=None
)
SAVED_SETTINGS: ContextVar[ty.Optional[config.SavedSettings]] = ContextVar(
    "saved_settings", default=None
)
SECRETS: ContextVar[ty.Optional[auth.Secrets]] = ContextVar("secrets", default=None)


def get_root_cfg() -> config.RootConfig:
    """
    Returns the current CLIContext. This can be used in CLI commands access "global" state
    which depends on the environment. During normal CLI operation, the context is provided
    by the __main__ entrypoint. During testing, it can be set manually.
    """
    context = ROOT_CONFIG.get()
    if context is None:
        raise RuntimeError("No CLI context set.")
    return context


def get_auth_state() -> auth.AuthState:
    cli_auth = AUTH_STATE.get()
    if cli_auth is None:
        ctx = get_root_cfg()
        cli_auth = auth.AuthStateImpl(ctx)

        AUTH_STATE.set(cli_auth)

    return cli_auth


def get_saved_settings() -> config.SavedSettings:
    saved_settings = SAVED_SETTINGS.get()
    if saved_settings is None:
        root_cfg = get_root_cfg()
        saved_settings = config.SavedSettings.from_file(root_cfg.saved_settings_path)

        SAVED_SETTINGS.set(saved_settings)

    return saved_settings


def get_secrets() -> auth.Secrets:
    secrets = SECRETS.get()
    if secrets is None:
        root_cfg = get_root_cfg()
        secrets = auth.FileSecrets.load(root_cfg.secrets_path)
        SECRETS.set(secrets)
    return secrets


def clear_state():
    ROOT_CONFIG.set(None)
    AUTH_STATE.set(None)
    SAVED_SETTINGS.set(None)
    SECRETS.set(None)


class UseSystemConfig:
    pass


@contextmanager
def cli_context(
    config_dir: ty.Union[ty.Path, UseSystemConfig] = UseSystemConfig(),
    auth: ty.Optional[auth.AuthState] = None,
    saved_settings: ty.Optional[config.SavedSettings] = None,
    secrets: ty.Optional[auth.Secrets] = None,
    inherit_context: bool = False,
):
    if config_dir is UseSystemConfig or isinstance(config_dir, UseSystemConfig):
        config_dir = config.global_config_dir()

    assignments = [
        (ROOT_CONFIG, config.RootConfig(config_dir=config_dir)),
        (AUTH_STATE, auth),
        (SAVED_SETTINGS, saved_settings),
        (SECRETS, secrets),
    ]
    with ExitStack() as cleanup:
        for var, value in assignments:
            if value is not None or not inherit_context:
                token = var.set(value)
                cleanup.callback(var.reset, token)
        yield
