#####################################################
#               BlocksOS Build Script               #
#####################################################
#             (c) James S Renwick 2014              #
#####################################################

from __future__ import print_function

HELP = """

Usage:
    build.py [opts...] [target]

    -verbose      Lowers the verbosity level to 0,
                  displaying all messages.

    --help        Prints this help message.
                  
    target        The build target to execute (e.g.
                  build, clean.) Defaults to 'main'.

"""

import os
import re
import sys

# Import the build manager
sys.path.append(".build")
from arran import *

# The tools to locate
TOOLS = [
    ("gcc", True),
    ("g++", True),
    ("ld",  True),
    ("nasm",False),
    ("bash",False)
]

# The resolved tool paths
PATHS = { }
# The collated and categorised files
FILES = { }

# Default incremental building to False
if not globals().has_key("INCREMENTAL"):
    INCREMENTAL = False

def get_tool_filename(tool):
    if TOOLCHAIN == None or TOOLCHAIN.strip() == "":
        return tool
    else:
        return TOOLCHAIN.strip() + "-" + tool

''' Attempts to resovle all required paths. '''
def find_tools():
    # Check through the list of tools
    for (tool,prefix) in TOOLS:
        toolpath = None
        
        # First look for a property
        try:
            toolpath = globals()["PATH_%s" %(tool.upper())].strip(" ")
        except :
            pass
        # If we've found a property, make sure it's valid
        if type(toolpath) == str and toolpath != "":
            if os.path.exists(toolpath):
                PATHS[tool] = toolpath # Save the path
                continue
            else:
                raise ValueError("An invalid path was given for '%s'" %(tool))
        # Otherwise look for a valid tool on the system path
        else:
            if prefix:
                PATHS[tool] = toolpath = search_path(get_tool_filename(tool))
            else:
                PATHS[tool] = toolpath = search_path(tool)
                
        # If none found still, raise an exception
        if type(toolpath) != str:
            raise ValueError("The tool '%s' could not be located" %(tool))
        else:
            log("Found '%s'" %(tool), LogLevel.vInfo)
            log("Path: '%s'" %toolpath, LogLevel.vInfo)


def get_files(srcpath):
    global FILES
    filter = FileFilter(srcpath)
    FILES  = filter.categorise(INCLUDES, EXCLUDES)

def needs_build(file, outExt=".o"):
    # Assume file exists and results in a .o file
    ofile = change_ext(file, outExt)
    if (os.path.exists(ofile)):
        return os.path.getmtime(file) >= os.path.getmtime(ofile)
    else:
        return True
    

def perform_init():
    new_section("preparing")
    find_tools()
    
    get_files("./")
    fcount = sum(map(len, FILES.values()))
    
    log("Including %s files"%fcount, LogLevel.vInfo)


def perform_assembly():
    new_section("assembling")

    # Assembly
    if FILES.has_key("asm-files"):        
        for file in FILES["asm-files"]:

            if INCREMENTAL and not needs_build(file,".s.o"):
                log ("Skipping '%s'"%file)
                continue
            
            log("Assembling '%s':"%file)
            
            # Set arguments
            args = [
                PATHS["nasm"],
                "-f", "elf",
                "-o", change_ext(file,".s.o")
            ]
            args.extend(ASMFLAGS)
            args.append(file)
            
            log(" ".join(args), LogLevel.vInfo)
            rc = start_process(args)

            log("Returned with code %s"%rc, LogLevel.vInfo)

    else:
        log("Not assembling assembly source", LogLevel.vInfo)


def perform_build():

    perform_assembly();
    
    new_section("compiling")

    # === C COMPILE ===

    if FILES.has_key("c-files"):
    
        args = ["-c", "-x", "c"]

        for macro in C_MACROS:
            args.append("-D")
            args.append(macro)
        for inc in C_INCLUDE_DIRS:
            args.append("-I")
            args.append(os.path.abspath(inc))

        for file in FILES["c-files"]:

            if INCREMENTAL and not needs_build(file):
                log ("Skipping '%s'"%file)
                continue
            
            log("Compiling '%s':"%file)

            a = [PATHS["gcc"]]
            a.extend(args)
            a.append("-o")
            a.append(change_ext(file,".o"))
            a.extend(CFLAGS)
            a.append(file)
            
            log(" ".join(a), LogLevel.vInfo)
            rc = start_process(a)
                       
            log("Returned with code %s"%rc, LogLevel.vInfo)
    else:
        log("Not compiling C source files", LogLevel.vInfo)

    # === C++ COMPILE ===

    if FILES.has_key("cpp-files"):
    
        args = ["-c", "-x", "c++"]

        for macro in CPP_MACROS:
            args.append("-D")
            args.append(macro)
        for inc in CPP_INCLUDE_DIRS:
            args.append("-I")
            args.append(os.path.abspath(inc))

        for file in FILES["cpp-files"]:

            if INCREMENTAL and not needs_build(file):
                log ("Skipping '%s'"%file)
                continue
            
            log("Compiling '%s':"%file)

            a = [PATHS["gcc"]]
            a.extend(args)
            a.append("-o")
            a.append(change_ext(file,".o"))
            a.extend(CPPFLAGS)
            a.append(file)
            
            log(" ".join(a), LogLevel.vInfo)
            rc = start_process(a)
                       
            log("Returned with code %s"%rc, LogLevel.vInfo)

    else:
        log("Not compiling C++ source files", LogLevel.vInfo)

    # === Link ===
    # Re-scan files
    new_section("linking")
    get_files("./")

    # Now link the object files
    if FILES.has_key("object-files"):

        args = [
            PATHS["ld"],
            "-T", LINKER_SCRIPT,
            "-o", OUTPUT_FILE,
            "-L", "./lib"
        ]
        args.extend(LINKFLAGS)
        
        args.append("-lcrti")
        args.append(os.path.join(GCC_LIB_PATH,"crtbegin.o"))
		
        for file in FILES["object-files"]:
            args.append(file)
	
	args.append(os.path.join(GCC_LIB_PATH,"crtend.o"))
	args.append("-lcrtn")

        log(" ".join(args), LogLevel.vInfo)
        rc = start_process(args)

        log("Returned with code %s"%rc, LogLevel.vInfo)
    else:
        log("Linking disabled, skipping", LogLevel.vInfo)

    # Make the bootable image
    perform_mkimg()

def perform_mkimg():
    new_section("creating image")

    args = [
        PATHS["bash"],
        "-c",
        "grub-mkrescue --output='"+os.path.abspath(OUTPUT_IMAGE)
        + "' '" + os.path.abspath(IMAGE_FOLDER) + "'"
    ]

    log(" ".join(args), LogLevel.vInfo)
    rc = start_process(args)

    log("Returned with code %s"%rc, LogLevel.vInfo)

def perform_clean():
    if not FILES.has_key("clean-files"):
        log("No files to clean", LogLevel.vInfo)
    else:
        for file in FILES["clean-files"]:
            try:
                os.remove(file)
                log("Removed file '%s'"%file, LogLevel.vInfo)
            except Exception as e:
                log("Error removing file '%s': %s"%(file,e), LogLevel.Warn)


# ==================================================

TARGET("main",    "build")
TARGET("clean",   perform_clean, [perform_init])
TARGET("build",   perform_build, [perform_init])
TARGET("rebuild", lambda:None,   ["clean", perform_build])
TARGET("assemble",perform_assembly,["clean"])

# ==================================================
if (__name__ == "__main__"):
    
    for i in range(1, len(sys.argv)):
        arg = sys.argv[i]

        # Look for optional args
        if arg.startswith("-") and arg == "--help":
            print(HELP)
            exit(0)

    # Execute the target
    run_target(get_start_target())

    
