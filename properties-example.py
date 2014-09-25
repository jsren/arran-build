# Example Properties File
# ------------------------
# Copy, edit & rename to "properties.py" before starting build

import os

# === Environment Parameters ===

FAILONERROR  = True                # Set to stop building upon external program error
INCREMENTAL  = True                # Set whether to enable incremental building
OUTPUT_FILE  = "a.out"             # The filename of the output file
PROJECT_NAME = "Project"           # The name of the project to build

TOOLCHAIN = None   # The cross-compiler prefix (w/o trailing '-')

# Add the GCC install dir to the process' PATH
#os.environ["PATH"] = os.path.abspath(GCC_PATH) + os.pathsep + os.environ["PATH"]

# === Build Parameters ===

SOURCE_DIRS = ["."] # Source code directories

# The files to include in the build
# Format  <file-regex> : [<category-name>,...]
INCLUDES = {
    ".*\\.c$"  : ["c-files"],
    ".*\\.cpp$": ["cpp-files"],
    ".*\\.o$"  : ["object-files", "clean-files"]
}

# The file(s) to exclude from the build
# Format  <file-regex>
EXCLUDES = [
    ".*[\\\\/]tmp[\\\\/].*", # Exclude all files in a directory named 'tmp'
]

# Initial macros (defines) for the C compiler
C_MACROS = [ "LANGC", "BITS32" ]

# Include directories for the C compiler
C_INCLUDE_DIRS = [
    ".",
    "./include"
]

# Flags passed to the C compiler
CFLAGS = [
    "-g",             # Set for debug builds
    "-Wall",          # Enables all warnings
    "-c",
    "-w",
    "-m32",
    "-march=i586"
]

# Initial macros (defines) for the C++ compiler
CPP_MACROS = [ "LANGCPP", "BITS32" ]

# Include directories for the C++ compiler
CPP_INCLUDE_DIRS = C_INCLUDE_DIRS

# Flags passed to the C++ compiler
CPPFLAGS = CFLAGS

# Flags to pass to the linker
LINKFLAGS = [
    "-m32",
    "-march=i586",
    "-Wall"
]
