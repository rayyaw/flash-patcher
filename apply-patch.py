#!/usr/bin/python3

import shutil
import subprocess
import sys
import os

# If you're not using the Flatpak version of JPEXS, you should change this to the absolute path of JPEXS (even if it's in $PATH)
JPEXS_PATH = "/usr/bin/flatpak"
# If you're not using the Flatpak version of JPEXS, you should change this to []
JPEXS_ARGS = ["run", "--branch=stable", "--arch=x86_64", "--command=ffdec.sh", "com.jpexs.decompiler.flash"]

def perror(mesg):
    print(mesg, file=sys.stderr)

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
    current_file = []

    add_line_no = 0
    current_line_no = 1
    
    for line in lines:
        line_stripped = line.strip("\n\r ")

        # Ignore comments and blank lines 
        if len(line_stripped) == 0 or line[0] == '#':
            continue
       
        # If we're not inside a line addition block, run the full parser
        if not line_add_mode:
            split_line = line_stripped.split()

            # Account for spaces in file name by taking everything except the first (command character) and last (line number/s) blocks
            short_name = ' '.join(split_line[1:-1])
            file_location = "./.Patcher-Temp/scripts/" + short_name
            
            # Add the current script to the list of modified ones (ie, keep this in the final output)
            modified_scripts.add(file_location)

            try:
                with open(file_location) as f:
                    current_file = f.readlines()
            except (FileNotFoundError, IsADirectoryError) as e:
                perror("")
                perror(patch_file + ", line " + str(current_line_no) + ": Invalid injection location")
                perror("Could not find or load SWF decompiled file at: " + file_location)
                perror("Aborting...")
                exit(1)

            # If we have an add command, set the adding location and switch to add mode
            if split_line[0] == "add":
                line_add_mode = True
                add_line_no = find_write_location(current_file, split_line[-1])

            # If we have a remove command, remove the specified line numbers (inclusive)
            elif split_line[0] == "remove":
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

            else:
                print("Unrecognized command: ", split_line[0], "skipping")
            
        # If we're in add mode and encounter the end of the patch, write the modified script back to file
        elif line == "end-patch\n":
            line_add_mode = False
            write_to_file(file_location, current_file)

        # If we're in add mode, insert the script into the line buffer
        else:
            current_file.insert(add_line_no, line)
            add_line_no += 1

        current_line_no += 1

    if line_add_mode:
        perror("")
        perror(file_location + ": Syntax error")
        perror("Missing end-patch for \"add\"")
        perror("Aborting...")
        exit(1)

    # Return the set of modified scripts, so we can aggregate in main()
    return modified_scripts

def main(inputfile, folder, stagefile, output):
    print("Riley's SWF Patcher - v1.4.0")

    # Decompile the swf into temp folder called ./.Patcher-Temp
    if not os.path.exists("./.Patcher-Temp"):
        os.mkdir("./.Patcher-Temp")

    if not os.path.exists(sys.argv[1]):
        perror("Could not locate the SWF file: " + sys.argv[1])
        perror("Aborting...")
        exit(1)
   
    try:
        decomp = subprocess.run([JPEXS_PATH] + JPEXS_ARGS + ["-export", "script", "./.Patcher-Temp", sys.argv[1]], \
            stdout=subprocess.DEVNULL, \
            stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        perror("Could not locate required dependency: JPEXS Flash Decompiler. Aborting...")
        exit(1)

    if (decomp.returncode != 0):
        perror("JPEXS was unable to decompile the SWF file: " + sys.argv[1])
        perror("Aborting...")
        exit(1)

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

        modified_scripts |= apply_patch(folder + "/" + patch_stripped)

    # Delete all non-modified scripts
    # Taken from https://stackoverflow.com/questions/19309667/recursive-os-listdir - Make recursive os.listdir
    scripts = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser("./.Patcher-Temp")) for f in fn]
    for script in scripts:
        if script not in modified_scripts:
            os.remove(script)

    print("Injection complete, recompiling...")

    # Repackage the file as a SWF
    # Rant: JPEXS should really return an error code if recompilation fails here! Unable to detect if this was successful or not otherwise.
    subprocess.run([JPEXS_PATH] + JPEXS_ARGS + ["-importScript", sys.argv[1], sys.argv[4], "./.Patcher-Temp"], \
            stdout=subprocess.DEVNULL)
    
    shutil.rmtree("./.Patcher-Temp")

    print("Done.")

if __name__ == "__main__":
    # command line argument checking
    if (len(sys.argv) != 5):
        perror("Usage:", sys.argv[0], "[SWF to patch] [patch folder] [patch stage file] [output SWF]")
        exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
