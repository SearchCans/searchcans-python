import os
import subprocess
import sys
from pathlib import Path


def test_account_smoke_requires_an_explicit_environment_key() -> None:
    root = Path(__file__).resolve().parents[1]
    environment = os.environ.copy()
    environment.pop("SEARCHCANS_API_KEY", None)

    result = subprocess.run(
        [sys.executable, "scripts/account_smoke.py"],
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "Set SEARCHCANS_API_KEY" in result.stderr
