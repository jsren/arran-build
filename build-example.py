#####################################################
#              Example GCC Build Script             #
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
from gcc_build import *


# The collated and categorised files
FILES = { }

def perform_init():
    global FILES
    
    new_section("preparing")

    # Search for files to build
    FILES = get_files(SOURCE_DIRS)

    fcount = sum(map(len, FILES.values()))    
    log("Including %s files"%fcount, LogLevel.vInfo)


def perform_build():
    global FILES
    
    new_section("compiling")

    # === C COMPILE ===

    if FILES.has_key("c-files"):
        compile_c(FILES["c-files"], ["-x", "c"])
    else:
        log("Not compiling C source files", LogLevel.vInfo)

    # === C++ COMPILE ===

    if FILES.has_key("cpp-files"):
        compile_cpp(FILES["cpp-files"], ["-x", "c++"])
    else:
        log("Not compiling C++ source files", LogLevel.vInfo)

    # === Link ===
    new_section("linking")

    # Refresh file list
    FILES = get_files(SOURCE_DIRS)

    # Now link the object files
    if FILES.has_key("object-files"):
        
        args = []
        args.extend(LINKFLAGS)
        args.extend(["-o", OUTPUT_FILE])
        
        for file in FILES["object-files"]:
            args.append(file)

        rc = invoke_gpp(args)
        log("Returned with code %s"%rc, LogLevel.vInfo)
    else:
        log("Linking disabled, skipping", LogLevel.vInfo)


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

# TARGET(NAME, FUNCTION)
# TARGET(NAME, FUNCTION, [DEPENDENCIES])

TARGET("main",    "build")
TARGET("clean",   perform_clean, [perform_init])
TARGET("build",   perform_build, [perform_init])
TARGET("rebuild", lambda:None,   ["clean", perform_build])

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

    
