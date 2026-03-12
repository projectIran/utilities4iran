import subprocess
import sys
from pathlib import Path


def test_cli_mode_requires_generator_and_fails_cleanly_when_missing():
    main_path = Path(__file__).resolve().parents[1] / "src" / "main.py"
    proc = subprocess.run(
        [sys.executable, str(main_path), "--cli"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )

    assert proc.returncode == 1
    assert "[ERROR] Unable to generate bridge at this time" in proc.stderr
    assert "Traceback" not in proc.stderr
