#!/usr/bin/env python3
"""
Conversion between `Named` and `Compact` layouts
"""
import sys
import h5py
from antmoc_mgxs.options import Options
import antmoc_mgxs.manip.h5 as manip


options = Options()

# Reset default values
options["input"].default = "./mgxs.h5"
options["output"].default = "./mgxs.converted.h5"

# Parse command line arguments
options.parse(sys.argv[1:])

# Check if we should print a help message
if options("help"):
    options.help()
    sys.exit(1)

inputlayout = options("layout").lower()
if inputlayout == "named":
    outputlayout = "compact"
else:
    outputlayout = "named"

with h5py.File(options("input"), 'r') as inputfile:
    with h5py.File(options("output"), 'w') as outputfile:
        manip.convert_layout(inputfile, outputfile, layout=inputlayout)

print(f"Successfully converted layout '{inputlayout}' to '{outputlayout}'")
print(f"The output file is '{options('output')}'")
