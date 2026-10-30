import subprocess
import sys
from pathlib import Path

DISTRIBUTIONS = {
    "wheel": "*.whl",
    "sdist": "*.tar.gz",
}


def main():
    distribution = sys.argv[1] if len(sys.argv) > 1 else "wheel"

    if len(sys.argv) > 2 or distribution not in DISTRIBUTIONS:
        sys.exit(
            f"Usage: {sys.argv[0]} [{'|'.join(DISTRIBUTIONS)}]"
        )

    packages = list(Path("dist").glob(DISTRIBUTIONS[distribution]))

    if len(packages) != 1:
        sys.exit(
            f"Expected exactly one {distribution} in dist/, "
            f"found {len(packages)}."
        )

    package = packages[0]

    print(f"Installing {distribution}: {package}")

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--force-reinstall",
            "--no-deps",
            str(package),
        ],
        check=True,
    )

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

if __name__ == "__main__":
    main()
