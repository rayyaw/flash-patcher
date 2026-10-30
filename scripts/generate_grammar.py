
from importlib.metadata import version as get_package_version
from pathlib import Path
import re
import shutil
import subprocess
from urllib.request import urlopen

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

def version_of_runtime() -> str:
    """Return the installed ANTLR Python runtime version."""
    return get_package_version("antlr4-python3-runtime")

def download_antlr(root: Path, antlr_version: str) -> Path:
    """Download and cache the matching ANTLR generator JAR."""
    if not re.fullmatch(r"\d+\.\d+\.\d+", antlr_version):
        raise RuntimeError(
            f"Unsupported ANTLR runtime version: {antlr_version}"
        )

    cache_dir = root / ".antlr"
    cache_dir.mkdir(parents=True, exist_ok=True)

    jar = cache_dir / f"antlr-{antlr_version}-complete.jar"

    if jar.is_file():
        return jar

    url = (
        "https://www.antlr.org/download/"
        f"antlr-{antlr_version}-complete.jar"
    )
    temporary_jar = cache_dir / f"antlr-{antlr_version}.tmp"

    try:
        print(f"Downloading ANTLR {antlr_version}...")
        with urlopen(url, timeout=60) as response:
            with temporary_jar.open("wb") as destination:
                shutil.copyfileobj(response, destination)

        temporary_jar.replace(jar)
    finally:
        temporary_jar.unlink(missing_ok=True)

    return jar

def generate_grammar(root: Path) -> None:
    """Generate Python parser files using the matching ANTLR version."""
    root = root.resolve()
    grammar_dir = root / "flash_patcher" / "antlr"
    output_dir = root / "flash_patcher" / "antlr_source"

    antlr_version = version_of_runtime()
    jar = download_antlr(root, antlr_version)

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating grammar with ANTLR {antlr_version}...")

    for grammar in ("PatchfileLexer.g4", "PatchfileParser.g4"):
        subprocess.run(
            [
                "java",
                "-jar",
                str(jar),
                "-Dlanguage=Python3",
                "-visitor",
                "-Xexact-output-dir",
                "-o",
                str(output_dir),
                str(grammar_dir / grammar),
            ],
            cwd=root,
            check=True,
        )

    print("Grammar generation complete.")

class CustomBuildHook(BuildHookInterface):
    """Hatch custom build hook, so this can be run as part of the build."""
    def initialize(self, version, build_data):
        generate_grammar(Path(self.root))

        # Include generated files, even if they are ignored by Git.
        build_data["artifacts"].extend([
            "flash_patcher/antlr_source/**/*.py",
            "flash_patcher/antlr_source/**/*.tokens",
            "flash_patcher/antlr_source/**/*.interp",
        ])


if __name__ == "__main__":
    generate_grammar(Path(__file__).resolve().parent.parent)
