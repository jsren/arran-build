#####################################################
#        GCC TOOLCHAIN HELPER VERSION 1.0.3         #
#####################################################
#             (c) James S Renwick 2014              #
#####################################################

from __future__ import print_function

import os
import sys

from . import *

# The tools to locate
TOOLS = [ ]
# The resolved tool paths
PATHS = { }


def compile_c(files, args=[], outExt=".o"):
    pre = []
    for macro in C_MACROS:
        pre.append("-D")
        pre.append(macro)
    for inc in C_INCLUDE_DIRS:
        pre.append("-I")
        pre.append(os.path.abspath(inc))
    pre.extend(CFLAGS)

    for file in files:
        if INCREMENTAL and not needs_build(file):
            log("Skipping '%s'"%file)
            continue
            
        log("Compiling '%s':"%file)
        a = []
        a.extend(pre)
        a.extend(args)
        a.append("-o")
        a.append(change_ext(file, outExt))
        a.append(file)

        rc = invoke_gcc(a)
        log("Returned with code %s"%rc, LogLevel.vInfo)

def compile_cpp(files, args=[], outExt=".o"):
    pre = []
    for macro in CPP_MACROS:
        pre.append("-D")
        pre.append(macro)
    for inc in CPP_INCLUDE_DIRS:
        pre.append("-I")
        pre.append(os.path.abspath(inc))
    pre.extend(CPPFLAGS)

    for file in files:
        if INCREMENTAL and not needs_build(file):
            log("Skipping '%s'"%file)
            continue
            
        log("Compiling '%s':"%file)
        a = []
        a.extend(pre)
        a.extend(args)
        a.append("-o")
        a.append(change_ext(file, outExt))
        a.append(file)

        rc = invoke_gpp(a)
        log("Returned with code %s"%rc, LogLevel.vInfo)

def make_library(files, output, args=[]):
    pre = ["rcsu", output]
    pre.extend(args)
    
    for file in files:
        pre.append(file)
    return invoke_tool("ar", pre)

def invoke_gcc(args):    
    return invoke_tool("gcc", args)

def invoke_gpp(args):
    return invoke_tool("g++", args)

def invoke_ld(args):
    return invoke_tool("ld", args)

def invoke_as(args):
    return invoke_tool("as", args)

def invoke_tool(tool, args):
    if not PATHS.has_key(tool):
        TOOLS.append((tool, True))
        find_tools(TOOLS, PATHS)
        
    a = [PATHS[tool]]
    a.extend(args)

    log(" ".join(a), LogLevel.vInfo)
    
    return start_process(a)


# ==================================================
if (__name__ == "__main__"):
    log("Arran Build System cannot be executed directly", LogLevel.Crit)
    exit(-1)

    
