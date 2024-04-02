# rayyaw's SWF Patcher

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

The patcher will take the input SWF, apply the commands specified in the top-level patch file (which must be located in the patch folder), and create the output SWF.

The recommended way to install Flash Patcher is through pip. You can do this with `pip install flash-patcher`.

If you want to build the Flash Patcher .whl file locally, run `cd build && make`. The .whl will be generated in the `dist/` folder. The `hatch` pip package is required to run the build. You can also run `make install` to install the package locally. **Note that this will run pip with `--break-system-packages` and `--force-reinstall` options, so use this at your own risk.**

The command line arguments are as follows:

### Required arguments
- `--inputswf`: The input SWF to use. You should create a base hack to avoid issues with Flash deobfuscation.
- `--folder`: The top-level folder where all your patch files are located.
- `--stagefile`: The top level patch file's path within the top level folder.
- `--outputswf`: The path to save the output swf (relative to the current path)

Example: `$PATCHER --inputswf $SWF_FILE_PATH/SMF_Base_Hack.swf --folder . --stagefile fullgame.patch --outputswf SMF-Fullgame-Build-$1.swf`

### Optional arguments
- `--invalidateCache`: Force the patcher to decompile the SWF. If this flag is not set, Flash Patcher may use a cached version of the SWF decompilation to speed up the process.
- `--all`: Recompile the full SWF. This is required when updating SWF content other than scripts, but slows down recompilation.
- `--xml`: Inject in xml mode. This decompiles the .swf to .xml and allows you to modify the xml file.

## File Structure

You should create the following file structure for your patches:

- Create a top-level patch folder. You will put all your files in this folder.
- Create one or more patch files. These contain the code to inject into the SWF.
- Create a main patch file. This will be the top-level one that will start execution.

### Patch Files

A patch file (usually ending in .patch) may look something like this:

```
# Comment

add DefineSprite_1058 boss2/DoAction.as 789
begin-patch
_root.gotoAndStop(15);
// cmd: skip 15
end-patch

remove frame_1/DoAction.as 789-1111
```

Every patch file consists of a set of commands, separated by newlines. You can use \# to write comments. The first parameter to any command is the file to modify (in this case, "DefineSprite_1058 boss2/DoAction.as" or "frame_1/DoAction.as"). To find the name of this, export all scripts using FFDec and make a note of the file name you want to modify.

### `add` command
You are allowed to put multiple `add` statements before a code block you wish to inject.

The first parameter to the add or remove command is always the name of the file to inject into.

The add and remove parameters can come in the following forms:
- `add file.as 567`. This will inject at line 567 in `file.as`.
- `add file.as end`. This will inject at the end of `file.as`.
- `add file.as function Mainfunc`. This will inject after the definition of `Mainfunc` in `file.as`.
- `add file.as function Mainfunc 15`. This will inject after the definition of `Mainfunc` in `file.as`, with an offset of 15 lines from the start of `Mainfunc`.

There is also an additional target:
```
add <filename>.as
begin-content
    // content to match. may be multiline.
end-content + <offset>
```

This will find the content in the `begin-content` block and inject on the line after the end of the content. The `+ <offset>` is optional, and specifies an integer offset (in lines) after the end of the content.

### `remove` command

Note that `remove` commands are inclusive of the final line.

Here is an example `remove` command. Note that you can still use the `function`, `content`, and `end` targets as shown above.

- `remove file.as 567-568`. This will remove lines 567 to 568 of `file.as`.

### `replace` command

Note that just like `add`, you can put multiple `replace` statements before a code block.

Here is an example `replace` command. Note that you can still use the `function` and `end` targets as shown above, as well as any `// cmd: ` commands.

```
replace file.as 3
begin-content
A
end-content
begin-patch
B
end-patch
```

This will look for the 3rd instance of `A` in `file.as`, and replace it with `B`.

Putting a function + offset of N instead of a raw number will find and replace the Nth instance of the content after the function header, and putting `end` will replace the last instance of the content.

Putting a `content` block instead of a raw number is unsupported and will cause the patcher to error out.

### `replace-all` command

As with the other commands, you can have multiple `replace-all` headers before the blocks. The syntax is mostly the same as the replace command, with the `content` and `patch` blocks operating in the same way. However, the header is changed:

```
replace-all file.as
```

We only need to specify the filename, as nothing else is used.

**Caveats**

There are several limitations that come with the `replace-all` command:

- You may not use both `replace` and `replace-all` headers for the same block, as this is invalid syntax.
- `replace-all` blocks do not support secondary commands.

### `add-asset` command

An `add-asset` command will look something like this:

```
# Comment
add-asset localfolder/derp.png images/8.png
```

This command takes the local file at `localfolder/derp.png` and copies it to `images/8.png` within the SWF. If there was already a file named `images/8.png`, it will be overwritten with the new file.

**Note:** Due to technical reasons, neither filepath in the `add-asset` command may contain spaces, dashes (`-`), or the equals sign (`=`).

### Variables and scoping

There are 2 ways of defining a variable to use later. Note that both the name and value of the variable are case sensitive.

1. `set-var varName=varValue`. This will declare a variable that you can use in the current patch, as well as any patch that is called within the current patch. (This will still work if you are multiple levels deep.)

2. `export-var varName=varValue`. This will declare a global variable that you can use in any patch.

Note that declaring a local variable will overwrite any previous values in the current scope, and declaring a global variable will overwrite the previous value of that global variable (if it exists), AND any previously set values of this variable in the current scope.

To call a named variable, simply use the following syntax:

`add ${varName}/file.as`

Note that all blocks where arbitrary text is allowed (ie, not specific formats like integers) support variables using simple string replacement, except location tokens (the line number or target specifying where inside of a file to inject). Arbitrary Python scripts also don't have access to variables.

Nested variable definitions are not allowed. For example, `set var1=${var2}` will set the value of `var1` to the **string literal** `${var2}` rather than the value of `var2`.

**Note:** Due to technical reasons, variable names and values may not contain dashes (`-`) or the equals sign (`=`).


### Content Insertion

For the add command, all lines up to (but not including) the `end-patch` command will be inserted into the SWF, *on* the specified line. For the remove command, all lines between the two numbers specified will be removed (and this is inclusive).

After one or more add commands, add a newline, a `begin-patch\n` and then enter your code block. At the end of the block, add a newline and `end-patch` to tell the patcher the patch is finished.

### Secondary commands

Within a code block, you can also use the following syntax to skip ahead within the file:
```
// cmd: skip N
```

Type `// cmd: skip ` (with spaces as shown), then the number of lines you wish to skip without modifying.

To inject while in XML mode, use normal `.patch` files, but the add location will be the hardcoded string `swf.xml`.

### Nested Patch Files

You can apply arbitrary patch files within the main file. These can be executed as follows:

```
apply-patch file.patch
```

### Python Files

Arbitrary Python scripts can be referenced in the patch file. They should be placed in the patch folder, and will be executed inside the decompiled directory.

The command looks like this: `exec-python file.py`.

You must respect the following API:

- Only Python 3 is supported.
- The name of the Python file must not contain spaces.
- You must print a list of files that are modified. This list must be comma-separated and formatted in UTF-8.

An example of such a list: `DoAction1.as, DoAction2.as`. Trailing whitespace or newlines are fine, as those will be stripped off.

The input to your Python program will be a list of variables in CFG format, passed through stdin. Here is an example of the stdin:

```
key1=val1
key2=val2

```

Note that a trailing newline may be present. Also note that both variable names and values may contain any character other than `-` or `=`, and you must handle all appropriate cases.

**Note:** Python files don't support modifying variables.

### Injection Order

Within each patchfile, the patches will be processed one block at a time, with each command being processed from the top of the file to the bottom. Note that if you are injecting multiple times into the same file, this means that you should inject bottom to top to avoid the line numbers changing as the file is being patched.

## Licensing

All versions of Flash Patcher up to and including 5.3.0 are made available under CC-BY SA 4.0. For more information, check https://creativecommons.org/licenses/by-sa/4.0 .

Flash Patcher v5.3.0 and onward are made available under AGPLv3.

For v5.3.0, you may pick either the CC-BY SA 4.0 license, or the AGPLv3 license. You may not mix and match from both, and you should explicitly state which license you are using.
