#!/usr/bin/python3

import argparse
import base64
import shutil
import subprocess
import sys
import os

"""
Riley's SWF patcher

Development: RileyTech
Bug testing: Creyon

Download and updates: https://github.com/rayyaw/flash-patcher

License: CC-BY SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0)

Dependencies: Python 3, JPEXS Decompiler (https://github.com/jindrapetrik/jpexs-decompiler/releases)

Inject arbitrary code, images, and more into existing SWFs!
See the README for documentation and license.
"""

JPEXS_PATH = ""
JPEXS_ARGS = []

CURRENT_VERSION = "v4.1.2"

DECOMP_LOCATION = "./.Patcher-Temp/mod/"
DECOMP_LOCATION_WITH_SCRIPTS = DECOMP_LOCATION + "scripts/"

"""
Set JPEXS_PATH and JPEXS_ARGS to the specified path and (optionally) args if JPEXS exists at the specified location.
Returns True if successful, and False otherwise.
"""
def set_jpexs_if_exists(path, args=[]):
    global JPEXS_PATH
    global JPEXS_ARGS

    if (os.path.exists(path)):
        JPEXS_PATH = path
        JPEXS_ARGS = args
        return True

    return False

"""
Detect JPEXS install location. Returns True if successful.
"""
def detect_jpexs():
    # apt install location
    if (set_jpexs_if_exists("/usr/bin/ffdec")):
        return True


    # flatpak install location
    if (set_jpexs_if_exists("/usr/bin/flatpak", ["run", "--branch=stable", "--arch=x86_64", "--command=ffdec.sh", "com.jpexs.decompiler.flash"])):
        # Detect if JPEXS is installed. The function call can only detect if Flatpak is installed
        testrun = subprocess.run([JPEXS_PATH] + JPEXS_ARGS + ["-help"], stdout=subprocess.DEVNULL)

        if (testrun.returncode == 0):
            return True

    # windows x32 install location
    if (set_jpexs_if_exists("C:\\Program Files(x86)\\FFDec\\ffdec.exe")):
        return True

    # windows x64 install location
    if (set_jpexs_if_exists("C:\\Program Files\\FFDec\\ffdec.exe")):
        return True

    return False

def perror(mesg):
    print(mesg, file=sys.stderr)

def read_from_file(file_location, patch_file, current_line_no):
    try:
        with open(file_location) as f:
            current_file = f.readlines()
            return current_file
    except (FileNotFoundError, IsADirectoryError) as e:
        perror("")
        perror(patch_file + ", line " + str(current_line_no) + ": Invalid injection location")
        perror("Could not find or load SWF decompiled file at: " + file_location)
        perror("Aborting...")
        exit(1)

def write_to_file(path, lines):
    with open(path, "w") as f:
        f.writelines(lines)

"""
Find the location in the file specified.
If code is an integer, it'll resolve to writing AFTER that line number.
If code is "end", it'll resolve to the end of that file.
"""
def find_write_location(lines, code):
    if (code == "end"):
        return len(lines)
    else:
        try:
            return int(code) - 1
        
        except ValueError:
            perror("")
            perror("Invalid add location: " + code)
            perror("Expected keyword or integer (got type \"str\")")
            perror("Aborting...")
            exit(1)

class FilePosition:
    def __init__(self, file_name):
        self.fileName = file_name
        self.lineNumber = 0

class CodeInjector:
    def __init__(self):
        self.files = []
        self.fileContents = {}
        self.injectLines = []
        self.startingLineNo = -1

    # Return the file name of the script being modified
    def addInjectionTarget(self, injection_info, patch_file, current_line_no):
        split_line = injection_info.split()
        short_name = ' '.join(split_line[1:-1])
        file_name = DECOMP_LOCATION_WITH_SCRIPTS + short_name

        file_content = read_from_file(file_name, patch_file, current_line_no)
        current_file = FilePosition(file_name)

        split_line = injection_info.split()

        current_file.lineNumber = find_write_location(file_content, split_line[-1])
        self.files.append(current_file)
        self.fileContents[file_name] = file_content
        return file_name

    def addInjectionLine(self, line, current_line_no):
        self.injectLines.append(line)

        if self.startingLineNo == -1:
            self.startingLineNo = current_line_no

    def inject(self):
        if len(self.injectLines) == 0:
            return
        
        # Inject into every file
        for file in self.files:
            patch_line_no = self.startingLineNo
            file_line_no = file.lineNumber

            for line in self.injectLines:
                line_stripped = line.strip("\n\r ")
                split_line = line_stripped.split()

                # Handle internal commands
                if split_line[0] == "//" and split_line[1] == "cmd:":
                    if split_line[2] == "skip":
                        try:
                            file_line_no += int(split_line[3])
                            continue
                        except ValueError:
                            perror("")
                            perror("Invalid skip amount: " + split_line[3])
                            perror("Expected integer (got type \"str\")")
                            perror("Aborting...")
                            exit(1)

                self.fileContents[file.fileName].insert(file_line_no, line)

                patch_line_no += 1
                file_line_no += 1
            
        for file, fileContent in self.fileContents.items():
            write_to_file(file, fileContent)

"""
Apply a single patch file.
patch_file parameter: The path to the patch file.
"""
def apply_patch(patch_file):
    modified_scripts = set()
    lines = []

    # Read all lines from file
    try:
        with open(patch_file) as f:
            lines = f.readlines()
    except FileNotFoundError:
        perror("Could not open Patchfile: " + patch_file)
        perror("Aborting...")
        exit(1)

    line_add_mode = False
    file_location = ""

    current_line_no = 1

    injector = None
    
    for line in lines:
        line_stripped = line.strip("\n\r ")

        # Ignore comments and blank lines 
        if len(line_stripped) == 0 or line[0] == '#':
            current_line_no += 1
            continue

        split_line = line_stripped.split()

        # HANDLE ADD STATEMENT ----
        # If we have an add command, set the adding location and switch to add mode
        if split_line[0] == "add":
            if injector is None:
                injector = CodeInjector()

            script = injector.addInjectionTarget(line_stripped, patch_file, current_line_no)
            modified_scripts.add(script)

        elif split_line[0] == "begin-patch":
            line_add_mode = True

        # If we're in add mode and encounter the end of the patch, write the modified script back to file
        elif line_stripped == "end-patch" and line_add_mode:
            line_add_mode = False

            if injector is None:
                perror("")
                perror(patch_file + ", line " + str(current_line_no) + ": Invalid syntax")
                perror("end-patch is not matched by any 'add' statements")
                exit(1)
            
            injector.inject()
            injector = None

        elif line_add_mode:
            injector.addInjectionLine(line, current_line_no)
        
        # HANDLE REMOVE STATEMENT ----
        elif split_line[0] == "remove":
                # Account for spaces in file name by taking everything except the first (command character) and last (line number/s) blocks
                short_name = ' '.join(split_line[1:-1])
                file_location = DECOMP_LOCATION_WITH_SCRIPTS + short_name
                
                # Add the current script to the list of modified ones (ie, keep this in the final output)
                modified_scripts.add(file_location)

                current_file = read_from_file(file_location, patch_file, current_line_no)
                line_counts = split_line[-1].split("-")

                if len(line_counts) != 2:
                    perror("")
                    perror(patch_file + ", line " + str(current_line_no) + ": Invalid syntax")
                    perror("Expected two integers, separated by a dash (-) (at " + line_stripped + ")")
                    perror("Aborting...")
                    exit(1)

                try:
                    line_start = int(line_counts[0])
                    line_end = int(line_counts[1])
                except ValueError:
                    perror("")
                    perror(patch_file + ", line " + str(current_line_no) + ": Invalid syntax")
                    perror("Invalid line numbers provided: " + split_line[-1])
                    perror("Aborting...")
                    exit(1)

                try:
                    for i in range(line_start, line_end + 1):
                        del current_file[line_start - 1]
                except IndexError:
                    perror("")
                    perror(patch_file + ", line " + str(current_line_no) + ": Out of range")
                    perror("Line number " + str(line_end) + " out of range for file " + file_location)
                    perror("Aborting...")
                    exit(1)

                write_to_file(file_location, current_file)

        # Unrecognized statement
        else:
            perror("Unrecognized command: '" + split_line[0] + "', skipping (at " + patch_file + ", line " + str(current_line_no) + ")")

        current_line_no += 1

    if line_add_mode:
        perror("")
        perror(patch_file + ": Syntax error")
        perror("Missing end-patch for \"add\" on line " + str(injector.startingLineNo - 1))
        perror("Aborting...")
        exit(1)

    # Return the set of modified scripts, so we can aggregate in main()
    return modified_scripts

def apply_assets(asset_file, folder):
    modified_files = set()
    lines = []

    try:
        with open(asset_file) as f:
            lines = f.readlines()
    except FileNotFoundError:
        perror("Could not open asset pack file at: " + asset_file)
        perror("Aborting...")
        exit(1)

    for line in lines:
        line_stripped = line.strip("\n\r")
        split_line = line_stripped.split(' ')

        if len(line_stripped) == 0 or line_stripped.startswith("#"): # Comment
            continue
            
        elif line.startswith("add-asset"):
            # Local copy of file, then remote
            local_name = split_line[1]
            remote_name = ' '.join(split_line[2:])
            remote_name = line_stripped.split(" ")[2]

            if not os.path.exists(folder + "/" + local_name):
                perror("Could not find asset: " + local_name)
                perror("Aborting...")
                exit(1)

            # Create folder and copy things over
            remote_folder = remote_name.split("/")[0]
            
            if not os.path.exists(DECOMP_LOCATION + remote_folder):
                os.mkdir(DECOMP_LOCATION + remote_folder)

            shutil.copyfile(folder + "/" + local_name, DECOMP_LOCATION + remote_name)

            modified_files.add(DECOMP_LOCATION + remote_name)
        
        else:
            print("Unrecognized command: ", line, "skipping")
    
    return modified_files

"""
Decompile the SWF and return the decompilation location.

This uses caching to save time.

inputfile: the SWF to decompile
invalidate_cache: if set to True, will force decompilation instead of using cached files
"""
def decompile_swf(inputfile, invalidate_cache, xml_mode):
    # Decompile the swf into temp folder called ./.Patcher-Temp/[swf name, base32 encoded]
    if not os.path.exists("./.Patcher-Temp"):
        os.mkdir("./.Patcher-Temp")

    if not os.path.exists(inputfile):
        perror("Could not locate the SWF file: " + inputfile)
        perror("Aborting...")
        exit(1)

    cache_location = "./.Patcher-Temp/" + base64.b32encode(bytes(inputfile, "utf-8")).decode("ascii")
    if xml_mode:
        global DECOMP_LOCATION
        global DECOMP_LOCATION_WITH_SCRIPTS

        cache_location = "./.Patcher-Temp/swf2.xml"

        DECOMP_LOCATION = "./.Patcher-Temp/swf.xml"
        DECOMP_LOCATION_WITH_SCRIPTS = "./.Patcher-Temp/"

    # Mkdir / check for cache
    if invalidate_cache or (not os.path.exists(cache_location)):
        if (not os.path.exists(cache_location) and not xml_mode):
            os.mkdir(cache_location)

        print("Beginning decompilation...")

        decomp = None

        if xml_mode:
            decomp = subprocess.run([JPEXS_PATH] + JPEXS_ARGS + ["-swf2xml", inputfile, cache_location], \
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
        else:
            decomp = subprocess.run([JPEXS_PATH] + JPEXS_ARGS + ["-export", "script", cache_location, inputfile], \
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if (decomp.returncode != 0):
            perror("JPEXS was unable to decompile the SWF file: " + inputfile)
            perror("Aborting...")
            exit(1)

    else:
        print("Detected cached decompilation. Skipping...")

    return cache_location

"""
Recompile the SWF after injection is complete.

inputfile: The base SWF to use for missing files
outputfile: The location to save the output
recompile_all: If this is set to False, will only recompile scripts
"""
def recompile_swf(inputfile, output, recompile_all, xml_mode):
    # Repackage the file as a SWF
    # Rant: JPEXS should really return an error code if recompilation fails here! Unable to detect if this was successful or not otherwise.
    if xml_mode:
        subprocess.run([JPEXS_PATH] + JPEXS_ARGS + ["-xml2swf", "./.Patcher-Temp/swf.xml", output, xml_mode], \
            stdout=subprocess.DEVNULL)
        return
    
    subprocess.run([JPEXS_PATH] + JPEXS_ARGS + ["-importScript", inputfile, output, DECOMP_LOCATION], \
            stdout=subprocess.DEVNULL)
    
    if recompile_all:
        subprocess.run([JPEXS_PATH] + JPEXS_ARGS + ["-importImages", output, output, DECOMP_LOCATION], \
            stdout=subprocess.DEVNULL)
        subprocess.run([JPEXS_PATH] + JPEXS_ARGS + ["-importSounds", output, output, DECOMP_LOCATION], \
            stdout=subprocess.DEVNULL)
        subprocess.run([JPEXS_PATH] + JPEXS_ARGS + ["-importShapes", output, output, DECOMP_LOCATION], \
            stdout=subprocess.DEVNULL)
        subprocess.run([JPEXS_PATH] + JPEXS_ARGS + ["-importText", output, output, DECOMP_LOCATION], \
            stdout=subprocess.DEVNULL)

def main(inputfile, folder, stagefile, output, invalidate_cache, recompile_all, xml_mode):
    print("Riley's SWF Patcher - " + CURRENT_VERSION)

    if detect_jpexs() == False:
        perror("Could not locate required dependency: JPEXS Flash Decompiler. Aborting...")
        exit(1)

    print("Using JPEXS at:", JPEXS_PATH)

    cache_location = decompile_swf(inputfile, invalidate_cache, xml_mode)

    # Copy the cache to a different location so we can reuse it
    if (os.path.exists(DECOMP_LOCATION)):
        try:
            shutil.rmtree(DECOMP_LOCATION)
        except NotADirectoryError:
            os.remove(DECOMP_LOCATION)

    try:
        shutil.copytree(cache_location, DECOMP_LOCATION)
    except NotADirectoryError:
        shutil.copy(cache_location, DECOMP_LOCATION)

    print("Decompilation finished. Beginning injection...")

    try:
        # Open the stage file and read list of all patches to apply
        with open(folder + "/" + stagefile) as f:
            patches_to_apply = f.readlines()
    except FileNotFoundError:
        perror("")
        perror("Could not open stage file: " + folder + "/" + stagefile)
        perror("Aborting...")
        exit(1)

    # Keep track of which scripts have been modified by patching
    modified_scripts = set()

    # Apply every patch, ignoring comments and empty lines
    for patch in patches_to_apply:
        patch_stripped = patch.strip("\r\n ")
        if len(patch_stripped) == 0 or patch_stripped[0] == '#':
            continue

        # Check file extension of file
        if patch_stripped.endswith(".patch"): # Patch (code) file
            modified_scripts |= apply_patch(folder + "/" + patch_stripped)
        elif patch_stripped.endswith(".assets"): # Asset Pack file
            modified_scripts |= apply_assets(folder + "/" + patch_stripped, folder)
        else:
            perror("The file provided ('" + patch_stripped + "') did not have a valid filetype.")
            perror("Aborting...")
            exit(1)

    # Delete all non-modified scripts
    # Taken from https://stackoverflow.com/questions/19309667/recursive-os-listdir - Make recursive os.listdir
    scripts = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(DECOMP_LOCATION)) for f in fn]
    for script in scripts:
        if script not in modified_scripts:
            os.remove(script)

    print("Injection complete, recompiling...")

    recompile_swf(inputfile, output, recompile_all, xml_mode)
    
    print("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--inputswf", dest="input_swf", type=str, required=True, help="Input SWF file")
    parser.add_argument("--folder", dest="folder", type=str, required=True, help="Folder with patch files")
    parser.add_argument("--stagefile", dest="stage_file", type=str, required=True, help="Stage file name")
    parser.add_argument("--outputswf", dest="output_swf", type=str, required=True, help="Output SWF file")
    
    parser.add_argument("--invalidateCache", dest="invalidate_cache", default=False, action="store_true", help="Invalidate cached decompilation files")
    parser.add_argument("--all", dest="recompile_all", default=False, action="store_true", help="Recompile the whole SWF (if this is off, only scripts will recompile)")
    parser.add_argument("--xml", dest="xml_mode", default=False, action="store_true", help="Inject into an XML decompilation instead of standard syntax")

    args = parser.parse_args()

    main(args.input_swf, args.folder, args.stage_file, args.output_swf, args.invalidate_cache, args.recompile_all, args.xml_mode)
