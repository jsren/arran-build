#####################################################
#        NASM TOOLCHAIN HELPER VERSION 1.0.0        #
#####################################################
#             (c) James S Renwick 2014              #
#####################################################

from __future__ import print_function

import os
import sys

from . import *

# The tools to locate
TOOLS = []
# The resolved tool paths
PATHS = {}

def assemble_nasm(files, args=[], format="elf", outExt=".o"):
    pre = ["-f", format]
    for macro in ASM_MACROS:
        pre.append("-d")
        pre.append(macro)
    for inc in ASM_INCLUDE_DIRS:
        pre.append("-i")
        pre.append(os.path.abspath(inc) + os.path.sep)
    pre.extend(ASMFLAGS)
    pre.extend(args)

    for file in files:
        if INCREMENTAL and not needs_build(file):
            log("Skipping '%s'"%file)
            continue
            
        log("Compiling '%s':"%file)
        a = []
        a.extend(pre)
        a.append(file)
        a.append("-o")
        a.append(change_ext(file, outExt))

        rc = invoke_nasm(a)
        log("Returned with code %s"%rc, LogLevel.vInfo)

def invoke_nasm(args):
    if not PATHS.has_key("nasm"):
        TOOLS.append(("nasm", False))
        find_tools(TOOLS, PATHS)

    a = [PATHS["nasm"]]
    a.extend(args)

    log(" ".join(a), LogLevel.vInfo)

    return start_process(a)
