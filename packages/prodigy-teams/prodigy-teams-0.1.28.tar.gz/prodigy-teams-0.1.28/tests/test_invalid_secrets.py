import tempfile
from pathlib import Path

import pytest

from prodigy_teams import auth, errors


def test_secrets_validation():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)

        (temp_dir / "secrets.json").write_text(
            """{
                "api_token": {"access_token": ""}
            }"""
        )

        with pytest.raises(
            errors.ProdigyTeamsParseSecretsError,
            match=r"The file may be out of date or corrupted",
        ):
            auth.FileSecrets.load(temp_dir / "secrets.json")
