import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from pytest import raises

# Add the 'src' directory to the Python path
# Not doing this causes import errors
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from exception_handle.dependency import DependencyError
from patcher import main

@patch('shutil.copytree')
@patch('parse.stage.StagefileManager.parse')
@patch('compile.compilation.CompilationManager.recompile')
@patch('compile.compilation.CompilationManager.decompile')
def test_main_success(
    mock_decompile: MagicMock,
    mock_recompile: MagicMock,
    mock_stagefile_parse: MagicMock,
    mock_shutil_copytree: MagicMock,
) -> None:
    
    inputfile = Path("input")
    outputfile = Path("test.swf")
    cache = Path("../test/testdata/")

    mock_decompile.return_value = cache
    mock_stagefile_parse.return_value = set([
        Path("../test/testdata/derppotato1")
    ])


    main(
        inputfile,
        Path("../test/testdata"),
        Path("Stage1.stage"),
        outputfile,
    )

    mock_decompile.assert_called_once_with(
        inputfile, drop_cache=False, xml_mode=False
    )

    mock_recompile.assert_called_once_with(
        Path('.Patcher-Temp/mod'), inputfile, outputfile, recompile_all=False, xml_mode=False
    )

    mock_stagefile_parse.assert_called_once_with()

    mock_shutil_copytree.assert_called_once_with(cache, Path("./.Patcher-Temp/mod/"))

@patch('compile.compilation.CompilationManager.__init__')
def test_main_failure_no_jpexs(mock_compilation_manager: MagicMock) -> None:
    mock_compilation_manager.side_effect = ModuleNotFoundError("no JPEXS")

    with raises(DependencyError):
        main(
            Path("input"),
            Path("../test/testdata"),
            Path("Stage1.stage"),
            Path("test.swf"),
        )

    mock_compilation_manager.assert_called_once_with()
