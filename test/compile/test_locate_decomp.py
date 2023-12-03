from __future__ import annotations

from pathlib import Path

from flash_patcher.compile.locate_decomp import get_decomp_locations

def test_locate_decomp_success_normal() -> None:
    decomp, decomp_with_scripts = get_decomp_locations(False)

    assert decomp == Path("./.Patcher-Temp/mod/")
    assert decomp_with_scripts == Path("./.Patcher-Temp/mod/scripts/")

def test_locate_decomp_success_xml() -> None:
    decomp, decomp_with_scripts = get_decomp_locations(True)

    assert decomp == Path("./.Patcher-Temp/swf.xml")
    assert decomp_with_scripts == Path("./.Patcher-Temp/")
