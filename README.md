arran-build
===========

A set of libraries with which you can quickly and easily create cross-platform build scripts.

####Features
 - Completely cross-platform
 - Filtered log system
 - Build target system with target dependencies
 - Build Properties file for easy build customisation
 - Automatic console colourisation
 - Automatically locates the necessary tools
 - Support for cross-compilation
 - Incremental build support

####Usage

######Properties File
```python

OUTPUT_FILE = "./bin/example.bin"

INCREMENTAL  = True
FAILONERROR  = True
PROJECT_NAME = "Example Project"

SOURCE_DIRS = ["."]

# key:   Regexes used to filter filepaths for inclusion.
# value: Array of categories to apply to the resulting files.
INCLUDES = {
    ".*\.c$"   : ["c-files"],
    ".*\.cpp$" : ["cpp-files"],
    ".*\.o$"   : ["clean-files", "object-files"]
}

# Regexes used to filter filepaths for exclusion
EXCLUDES = {
    ".*\.ignore.*"
}

C_MACROS   = ["LANGC"]
CPP_MACROS = ["LANGCPP"]

C_INCLUDE_DIRS   = [ ]
CPP_INCLUDE_DIRS = [ ]

CFLAGS = [ ]

CPPFLAGS = [
    "-c",
    "-g",
    "-std=c++11",
    "-Wall"
]

```

######Build Script

```python

# Import build libs
#from arran import *

# If you're using gcc, import this instead
from arran.gcc import *


# Properties file (properties.py) automatically imported
```

```python

FILES = get_files(SOURCE_DIRS)

```

```python
log("Your debug msg here", LogLevel.vInfo)
log("Your message here",   LogLevel.Info)
log("Your warning here",   LogLevel.Warn)
log("Your error here",     LogLevel.Error)
```

```python
def my_function():
   new_section("doing something")
   
   # Do something here
   log("Something done", LogLevel.vInfo)
   
   # If we're using gcc:
   compile_cpp(FILES["cpp-files"])
   compile_c(FILES["c-files"], ["-x", "c"], ".o")
   
   rc = invoke_gpp(LINKFLAGS.extend(["example.o"]))
   log("Returned with code %s"%rc, LogLevel.vInfo)
   
   
   
```

```python
# ========================
TARGET("main", "build")      # Creates the default target 'main' which runs the target 'build'
TARGET("build", my_function) # Creates the target 'build' which runs the function my_function
```

```python
if (__name__ == "__main__"):
    run_target(get_start_target()) # Begins execution
```

####Screenshots

######Performing a rebuild.
![build.py rebuild](http://i.imgur.com/WXkS6Bc.png)

######Rebuilding with output set to verbose.
![build.py rebuild -verbose](http://i.imgur.com/65csCH1.png)

