from pathlib import Path

def get_decomp_locations(xml_mode: bool) -> (Path, Path):
    """Return (DECOMP_LOCATION, DECOMP_LOCATION_WITH_SCRIPTS)"""
    if xml_mode:
        return Path("./.Patcher-Temp/swf.xml"), Path("./.Patcher-Temp/")

    return Path("./.Patcher-Temp/mod/"), Path("./.Patcher-Temp/mod/scripts/")
