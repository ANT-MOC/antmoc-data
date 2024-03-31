#!/usr/bin/env python3

"""An example for exporting log files to json files.

This script takes options "--savedb".
"""

# sys.argv
import sys
import timeit
from antmocdata.log import Options, LogDB

# Parser for command line arguments
options = Options()

# Reset the default value
options["savedb"].default = "antmoc-logdb/"

# Parse command line arguments
options.parse(sys.argv[1:])

# Check if we should print a help message
if options("help"):
    options.help()
    exit(1)

# Initialize a LogDB
logdb = LogDB()
logdb.setup(options)

t_start = timeit.default_timer()

# Read log files and dump them into json files
logdb.save(options("savedb"))

t_stop = timeit.default_timer()
print(f"Time = {(t_stop - t_start):.3f} s")
