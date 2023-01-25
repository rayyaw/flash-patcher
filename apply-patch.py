#!/usr/bin/python3

import sys
import os

# If you're not using the Flatpak version of JPEXS, you should change this to "ffdec"
JPEXS_PATH = "/usr/bin/flatpak run --branch=stable --arch=x86_64 --command=ffdec.sh com.jpexs.decompiler.flash " 

def write_to_file(path, lines):
    with open(path, "w") as f:
        f.writelines(lines)

"""
Apply a single patch file.
patch_file parameter: The path to the patch file.
"""
def apply_patch(patch_file):
    modified_scripts = set()
    lines = []
    # Read all lines from file
    with open(patch_file) as f:
        lines = f.readlines()
    
    line_add_mode = False
    file_location = ""
    current_file = []

    add_line_no = 0
    
    for line in lines:
        line_stripped = line.strip("\n\r ")

        # Ignore comments and blank lines 
        if len(line_stripped) == 0 or line[0] == '#':
            continue
       
        # If we're not inside a line addition block, run the full parser
        if not line_add_mode:
            split_line = line_stripped.split()

            # Account for spaces in file name by taking everything except the first (command character) and last (line number/s) blocks
            short_name = ''.join(split_line[1:-1])
            file_location = ".Patcher-Temp/scripts/" + short_name
            
            # Add the current script to the list of modified ones (ie, keep this in the final output)
            modified_scripts.add(short_name.split("/")[0])

            with open(file_location) as f:
                current_file = f.readlines()

            # If we have an add command, set the adding location and switch to add mode
            if split_line[0] == "add":
                line_add_mode = True
                add_line_no = int(split_line[-1]) - 1

            # If we have a remove command, remove the specified line numbers (inclusive)
            elif split_line[0] == "remove":
                line_counts = split_line[-1].split("-")

                line_start = int(line_counts[0])
                line_end = int(line_counts[1])

                for i in range(line_start, line_end + 1):
                    del current_file[line_start - 1]
                
                write_to_file(file_location, current_file)

            else:
                print("Invalid command", split_line[0], "skipping")
            
        # If we're in add mode and encounter the end of the patch, write the modified script back to file
        elif line == "end-patch\n":
            line_add_mode = False
            write_to_file(file_location, current_file)

        # If we're in add mode, insert the script into the line buffer
        else:
            current_file.insert(add_line_no, line)
            add_line_no += 1

    # Return the set of modified scripts, so we can aggregate in main()
    return modified_scripts

def main(inputfile, folder, stagefile, output):
    print("Riley's SWF Patcher - v1.0.0")
    print("requirements: You must install JPEXS Free Flash Decompiler to run this patcher")

    # Decompile the swf into temp folder called ./.Patcher-Temp
    os.system("mkdir .Patcher-Temp")
    os.system(JPEXS_PATH + "-export script `pwd`/.Patcher-Temp " + sys.argv[1] + " > /dev/null")

    # Open the stage file and read list of all patches to apply
    with open(folder + "/" + stagefile) as f:
        patches_to_apply = f.readlines()

    # Keep track of which scripts have been modified by patching
    modified_scripts = set()

    # Apply every patch, ignoring comments and empty lines
    for patch in patches_to_apply:
        patch_stripped = patch.strip("\r\n ")
        if len(patch_stripped) == 0 or patch_stripped[0] == '#':
            continue

        modified_scripts |= apply_patch(folder + "/" + patch_stripped)

    # Delete all non-modified scripts
    scripts = os.listdir("./.Patcher-Temp/scripts")
    for script in scripts:
        if script not in modified_scripts:
            os.system('rm -r "./.Patcher-Temp/scripts/' + script + '"')

    # Repackage the file as a SWF
    os.system(JPEXS_PATH + "-importScript " + sys.argv[1] + " " + sys.argv[4] + " `pwd`/.Patcher-Temp")
    os.system("rm -r .Patcher-Temp")

if __name__ == "__main__":
    # command line argument checking
    if (len(sys.argv) != 5):
        print("Usage:", sys.argv[0], "[SWF to patch] [patch folder] [patch stage file] [output SWF]")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
