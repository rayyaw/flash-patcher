from __future__ import annotations

import sys
import os
from pathlib import Path

# Add the 'src' directory to the Python path
# Not doing this causes import errors
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from compile.locate_decomp import get_decomp_locations

def test_locate_decomp_success_normal() -> None:
    decomp, decomp_with_scripts = get_decomp_locations(False)

    assert decomp == Path("./.Patcher-Temp/mod/")
    assert decomp_with_scripts == Path("./.Patcher-Temp/mod/scripts/")

def test_locate_decomp_success_xml() -> None:
    decomp, decomp_with_scripts = get_decomp_locations(True)

    assert decomp == Path("./.Patcher-Temp/swf.xml")
    assert decomp_with_scripts == Path("./.Patcher-Temp/")
