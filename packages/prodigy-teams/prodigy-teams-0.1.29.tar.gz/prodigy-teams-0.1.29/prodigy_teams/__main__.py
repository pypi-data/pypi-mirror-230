import os
from pathlib import Path

FILE = Path(__file__).parent / "ptc.json"
IS_DEBUG = "_PTC_DEBUG" in os.environ

# IMPORTANT: This is the function exposed via the console_scripts entry point to
# register the "ptc" command and it's also referenced in the Dockerfile.all.
# Do not change its name unless necessary, and double-check that
# prodigy_teams.__main__.main is updated everywhere else.


def main() -> None:
    from radicli import StaticRadicli

    static = StaticRadicli.load(FILE, debug=IS_DEBUG)
    static.run()

    from . import config
    from .commands._state import ROOT_CONFIG
    from .main import cli

    if ROOT_CONFIG.get(None) is None:
        ROOT_CONFIG.set(config.RootConfig(config_dir=config.global_config_dir()))

    try:
        cli.run()
    except Exception:
        if IS_DEBUG:
            import pdb

            pdb.post_mortem()
        raise


if __name__ == "__main__":
    main()
