from pathlib import Path
import shutil

ANTLR_SOURCE = Path("flash_patcher/antlr_source")

for item in ANTLR_SOURCE.iterdir():
    if item.name == ".gitkeep":
        continue

    if item.is_dir():
        shutil.rmtree(item)
    else:
        item.unlink()

shutil.rmtree('flash-patcher-tests', ignore_errors=True)
shutil.rmtree('dist', ignore_errors=True)

