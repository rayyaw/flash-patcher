# Riley's SWF Patcher

### CI/CD
[![Pylint](https://github.com/rayyaw/flash-patcher/actions/workflows/pylint.yml/badge.svg)](https://github.com/rayyaw/flash-patcher/actions/workflows/pylint.yml)
[![Unit Tests](https://github.com/rayyaw/flash-patcher/actions/workflows/unittest.yml/badge.svg)](https://github.com/rayyaw/flash-patcher/actions/workflows/unittest.yml)
[![Integration Tests](https://github.com/rayyaw/flash-patcher/actions/workflows/integrationtest.yml/badge.svg)](https://github.com/rayyaw/flash-patcher/actions/workflows/integrationtest.yml)

### PyPI
[![PyPI Version](https://img.shields.io/pypi/v/flash-patcher.svg?logo=pypi&label=PyPI&logoColor=gold)](https://pypi.org/project/flash-patcher/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/flash-patcher.svg?logo=python&label=Python&logoColor=gold)](https://pypi.org/project/flash-patcher/)


## Requirements

### Build Dependencies

To compile this project yourself, you must install ANTLR. You can view more information at https://www.antlr.org/. For most linux distributions, this will be available as `antlr4` through your package manager.

### Runtime Dependencies

You must install JPEXS Free Flash Decompiler to use this patcher. For more information, check https://github.com/jindrapetrik/jpexs-decompiler. This will need to be installed manually.

Flash Patcher will automatically detect your FFDec install location.

You must have Python 3.10 or greater on your system to run this script, including the `antlr4-python3-runtime` pip package. This will be installed and verified automatically when installing through pip.

## Testing

To run unit tests, simply run `make test` from the `build` folder. You must have `pytest` and `coverage` installed to run unit tests.

## Installing and running

To apply a patch, run the `flash-patcher` command.

The patcher will take the input SWF, apply the patches specified in the stage file (which must be located in the patch folder), and create the output SWF.

The recommended way to install Flash Patcher is through pip. You can do this with `pip install flash-patcher`.

If you want to build the Flash Patcher .whl file locally, run `cd build && make wheel`. The .whl will be generated in the dist/ folder. The `hatch` pip package is required to run the build.

If you want to build from source, you should then use `pip` to install the generated wheel file in `dist`,

The command line arguments are as follows:

### Required arguments
- `--inputswf`: The input SWF to use. You should create a base hack to avoid issues with Flash deobfuscation.
- `--folder`: The top-level folder where all your patch, asset, and stage files are located.
- `--stagefile`: The stage file's path within the top level folder.
- `--outputswf`: The path to save the output swf (relative to the current path)

Example: `$PATCHER --inputswf $SWF_FILE_PATH/SMF_Base_Hack.swf --folder . --stagefile fullgame.stage --outputswf SMF-Fullgame-Build-$1.swf`

### Optional arguments
- `--invalidateCache`: Force the patcher to decompile the SWF. If this flag is not set, Flash Patcher may use a cached version of the SWF decompilation to speed up the process.
- `--all`: Recompile the full SWF. This is required when injecting asset packs but slows down recompilation.
- `--xml`: Inject in xml mode. This decompiles the .swf to .xml and allows you to modify the xml file.

## File Structure

You should create the following file structure for your patches:

- Create a top-level patch folder. You will put all your files in this folder.
- Create one or more patch stage files. These specify which patches to apply.
- Create one or more patch files. These contain the code to inject into the SWF.

### Patch Stage Files

A patch stage file (usually ending in .stage), may look something like this:

```
# Comment

patch1.patch
subfolder/patch2.patch
subfolder/pack.assets
```

You can use \# to comment out certain lines. Each line contains a patch file to run, and each injected file must be in the same top-level patch folder as the stage file. When the patcher runs, it will apply each patch file in order.

### Patch Files

A patch file (which must end in .patch), may look something like this:

```
# Comment

add DefineSprite_1058 boss2/DoAction.as 789
begin-patch
_root.gotoAndStop(15);
// cmd: skip 15
end-patch

remove frame_1/DoAction.as 789-1111
```

You can use \# to write comments. There are two types of commands, `add` and `remove`. The first parameter to any command is the file to modify (in this case, "DefineSprite_1058 boss2/DoAction.as" or "frame_1/DoAction.as"). To find the name of this, export all scripts using FFDec and make a note of the file name you want to modify.

You are allowed to put multiple `add` statements before a code block you wish to inject.

The second argument is a line number. For the add command, all lines up to (but not including) the `end-patch` command will be inserted into the SWF, *on* the specified line. For the remove command, all lines between the two numbers specified will be removed (and this is inclusive).

After one or more add commands, add a newline, a `begin-patch\n` and then enter your code block. At the end of the block, add a newline and `end-patch` to tell the patcher the patch is finished.

Instead of a line number, you can also specify `end` to append to the end of the file. This only applies for add commands.

Within a code block, you can also use the following syntax to skip ahead within the file:
```
// cmd: skip N
```

Type `// cmd: skip ` (with spaces as shown), then the number of lines you wish to skip without modifying.

To inject while in XML mode, use normal `.patch` files, but the add location will be the hardcoded string `swf.xml`.

### Asset Packs

An asset pack file (which must end in .assets), contains instructions on assets to inject into the Flash file. Currently supported types include:

- Images
- Sounds
- Shapes
- Text

The file will look something like this:

```
# Comment
add-asset localfolder/derp.png images/8.png
```

This asset pack file takes the local file at `localfolder/derp.png` and copies it to `images/8.png` within the SWF. If there was already a file named `images/8.png`, it will be overwritten with the new file.

## Licensing

This code is made available under CC-BY SA 4.0. For more information, check https://creativecommons.org/licenses/by-sa/4.0 .
