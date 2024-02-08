from pathlib import Path
from unittest.mock import MagicMock, patch

from pytest import raises

from flash_patcher.exception.dependency import DependencyError
from flash_patcher.patcher import main

@patch('shutil.copytree')
@patch('flash_patcher.parse.patch.PatchfileManager.parse')
@patch('flash_patcher.compile.compilation.CompilationManager.recompile')
@patch('flash_patcher.compile.compilation.CompilationManager.decompile')
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

@patch('flash_patcher.compile.compilation.CompilationManager.__init__')
def test_main_failure_no_ffdec(mock_compilation_manager: MagicMock) -> None:
    mock_compilation_manager.side_effect = ModuleNotFoundError("no FFDec")

    with raises(DependencyError):
        main(
            Path("input"),
            Path("../test/testdata"),
            Path("Stage1.stage"),
            Path("test.swf"),
        )

    mock_compilation_manager.assert_called_once_with()
