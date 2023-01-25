# Riley's SWF Patcher

## Requirements

You must install JPEXS Free Flash Decompiler to use this patcher. For more information, check https://github.com/jindrapetrik/jpexs-decompiler .

If you do not install via Flatpak, you should go into apply-patch.py and change `JPEXS-PATH` to your JPEXS executable, adding a space at the end of the string.

You must have Python 3 on your system to run this script. If you are running on Windows, you must use WSL to run this script.

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
```

You can use \# to comment out certain lines. Each line contains a patch file to run, and each patch file must be in the same top-level patch folder as the stage file. When the patcher runs, it will apply each patch file in order.

### Patch Files

A patch file (usually ending in .patch), may look something like this:

```
# Comment

add DefineSprite_1058 boss2/DoAction.as 789
_root.gotoAndStop(15);
end-patch

remove frame_1/DoAction.as 789-1111
```

You can use \# to write comments. There are two types of commands, `add` and `remove`. The first parameter to any command is the file to modify (in this case, "DefineSprite_1058 boss2/DoAction.as" or "frame_1/DoAction.as"). To find the name of this, export all scripts using JPEXS and make a note of the file name you want to modify.

The second argument is a line number. For the add command, all lines up to (but not including) the `end-patch` command will be inserted into the SWF, *after* the specified line. For the remove command, all lines between the two numbers specified will be removed (and this is inclusive).

After an add command, add a newline and then enter your code block. At the end of the block, add a newline and `end-patch` to tell the patcher the patch is finished.


## Applying Patches

To apply a patch, run the following command:

`./apply-patch.py [input SWF] [patch folder] [patch stage file] [output SWF]`

The patcher will take the input SWF, apply the patches specified in the stage file (which must be located in the patch folder), and create the output SWF.

## Licensing

This code is made available under CC-BY SA 4.0. For more information, check https://creativecommons.org/licenses/by-sa/4.0 .
