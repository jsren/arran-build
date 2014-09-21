#####################################################
#         Arran Build Engine Version 1.2.0          #
#####################################################
#             (c) James S Renwick 2014              #
#####################################################

from __future__ import print_function

import os
import sys
import re
import subprocess

# ======= Import properties without compiling if possible ========
try:
    if hasattr(sys, "dont_write_bytecode") and not sys.dont_write_bytecode:
        sys.dont_write_bytecode = True
        from properties import *
        sys.dont_write_bytecode = False
    else:
        from properties import *
except:
    pass

# ======== Provides colourising for console output ==========
from colorama import Back, Fore, Style, init as colorama_init

colorama_init()
print(Style.BRIGHT)
# ===========================================================


print ("""
__________Arran Build System__________

Version 1.0.0 (c) James S Renwick 2014
""")


# Contains the build targets
__TARGETS = {}

# Set the default verbosity
VERBOSITY = 1

# Cygwin stuff
os.environ["CYGWIN"] = "nodosfilewarning"


def change_ext(path, ext):
    i = path.rfind('.')
    
    if i != -1:
        path = path[0:i]
    return path + ext



class LogLevel:
    vInfo  = 0 # Verbose info
    Info   = 1
    Warn   = 2
    Error  = 3
    Output = 4
    Crit   = 5 # Critical error
    

def log(string, level = LogLevel.Info):
    if VERBOSITY > level:
        return
    
    if level == LogLevel.vInfo or level == LogLevel.Info:
        print("[%sINFO%s ] %s"%(Fore.CYAN,Fore.RESET,string))
    elif level == LogLevel.Warn:
        print("[%sWARN%s ] %s"%(Fore.YELLOW,Fore.RESET,string))
    elif level == LogLevel.Error:
        print("[%sERROR%s] %s"%(Fore.RED,Fore.RESET,string))
        exit(-1)
    elif level == LogLevel.Crit:
        print("[CRIT ] "+string, file=sys.stderr)
        exit(-1)
    elif level == LogLevel.Output:
        print(string)
    else:
        log("Unkown log level", LogLevel.Warn)


def start_process(args):
    proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
    (out, err) = proc.communicate()

    for line in out.splitlines():
        log(Style.NORMAL+line+Style.BRIGHT, LogLevel.Output)
    for line in err.splitlines():
        log(Style.NORMAL+Fore.RED+line+Fore.RESET+Style.BRIGHT, LogLevel.Output)
        
    return proc.returncode

class FileFilter:
    
    def __init__(self, baseDir):
        self.basedir = baseDir

    def filter(self, includes, excludes):
        cats = { }
        for reg in includes:
            cats[reg] = [""]
        return self.categorise(cats, excludes)

    def categorise(self, includes, excludes):
        output = { }
        # Add empty lists for each category
        for key in includes.iterkeys():
            for cat in includes[key]:
                if not output.has_key(cat):
                    output[cat] = []

        # Enumerate files and directories
        for (dir, subdirs, files) in os.walk(self.basedir):
            for file in files:
                file = os.path.join(dir, file)

                add        = False
                categories = None

                # Check the include regexes
                for regex in includes.iterkeys():
                    if re.match(regex, file) != None:
                        add        = True
                        categories = includes[regex]
                        break

                # Make sure it's not excluded
                for exreg in excludes:
                    if re.match(exreg, file) != None:
                        add = False
                        break

                # Add the file to the required categories        
                if add:
                    for category in categories:
                            output[category].append(file)
        return output

def search_path(file):
    output = None
    for dir in os.environ["PATH"].split(os.pathsep):
        p = os.path.join(dir, file)
        # Found a valid one
        if os.path.exists(p):
            output = p
            break
        # Check for default path extensions on Windows
        if os.name == "nt":
            for ext in os.environ["PATHEXT"].split(os.pathsep):
                if os.path.exists(p+ext):
                    output = p+ext
                    break
        # Linux/OSX is more difficult - I'll ignore this for now.
        # The paths will have to match perfectly or be given as
        # properties.
    return output

def new_section(name):
    log("\n%s:\n"%name, LogLevel.Output)

def TARGET(name, func, dependencies = []):
    __TARGETS[name] = [func, dependencies]

def run_target(name):
    (func, deps) = __TARGETS[name]

    log("Executing target '%s'"%name, LogLevel.vInfo)
    
    # Execute dependencies
    for dep in deps:
        if type(dep) == str:
            run_target(dep)
        elif callable(dep):
            dep()
        else: log("Cannot execute target '%s'"%name, LogLevel.Error)
            
    # Now execute target
    if type(func) == str:
        run_target(func)
    elif callable(func):
        func()
    else: log("Cannot execute target '%s'"%name, LogLevel.Error)


def get_start_target():    
    start_target = None
    
    for i in range(1, len(sys.argv)):
        arg = sys.argv[i]
                
        # Look for the target to execute
        if not arg.startswith("-"):
            if __TARGETS.has_key(arg):
                if start_target == None:
                    start_target = arg
                else:
                    log("More than one target specified", LogLevel.Error)
            else:
                log("Unknown target '%s'"%arg, LogLevel.Error)
                
    # Run "main" by default
    if start_target == None:
        start_target = "main"
        
    return start_target

# ==================================================
if __name__ == "__main__":
    log("Arran Build System cannot be executed directly", LogLevel.Crit)
    exit(-1)

else:
    for i in range(1, len(sys.argv)):
        arg = sys.argv[i]

        # Look for optional args
        if arg.startswith("-"):
            if arg == "-verbose":
                VERBOSITY = 0
