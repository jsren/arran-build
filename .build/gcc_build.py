#####################################################
#               GCC TOOLCHAIN HELPER                #
#####################################################
#             (c) James S Renwick 2014              #
#####################################################

from __future__ import print_function

import os
import re
import sys

from arran import *

# The tools to locate
TOOLS = [
    ("gcc", True)
]

CROSS = False

if globals().has_key("TOOLCHAIN"):
    CROSS = (TOOLCHAIN != None) and (TOOLCHAIN.strip() != "")


# The resolved tool paths
PATHS = { }

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
            log ("Skipping '%s'"%file)
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
            log ("Skipping '%s'"%file)
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
        find_tools()
        
    a = [PATHS[tool]]
    a.extend(args)

    log(" ".join(a), LogLevel.vInfo)
    
    return start_process(a)


def needs_build(file, outExt=".o"):
    # Assume file exists and results in a .o file
    ofile = change_ext(file, outExt)
    if (os.path.exists(ofile)):
        return os.path.getmtime(file) >= os.path.getmtime(ofile)
    else:
        return True

# ==================================================
if (__name__ == "__main__"):
    log("Arran Build System cannot be executed directly", LogLevel.Crit)
    exit(-1)

    
