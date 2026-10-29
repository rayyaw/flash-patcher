import subprocess
import sys
from pathlib import Path

# Install the built wheel.
wheels = list(Path("dist").glob("*.whl"))

if len(wheels) != 1:
    sys.exit(f"Expected exactly one wheel in dist/, found {len(wheels)}.")

subprocess.run(
    [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--force-reinstall",
        "--no-deps",
        str(wheels[0]),
    ],
    check=True,
)

# Clone the integration tests if they don't already exist.
tests_dir = Path("flash-patcher-tests")

if not tests_dir.is_dir():
    subprocess.run(
        [
            "git",
            "clone",
            "--recurse-submodules",
            "https://github.com/rayyaw/flash-patcher-tests.git",
            str(tests_dir),
        ],
        check=True,
    )
