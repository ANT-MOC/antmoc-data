#!/usr/bin/env python3
"""
Try to make cross-section arrays consistent
"""
import os
import sys
import h5py
from antmoc_mgxs.options import Options
import antmoc_mgxs.manip.h5 as manip


options = Options()

# Additional options
options.add(name="fix", default="sigma_s", doc="Fix cross-sections (sigma_s, sigma_t)")

# Reset default values
options.opts("input").default = "./mgxs.h5"
options.opts("output").default = "./mgxs.fixed.h5"

# Parse command line arguments
options.parse(sys.argv[1:])

# Check if we should print a help message
if options["help"]:
    options.help()
    sys.exit(1)

inputpath = os.path.abspath(options["input"])
outputpath = os.path.abspath(options["output"])

if inputpath == outputpath:
    raise ValueError(f"Use the input file as the output is not permitted: {inputpath}")

with h5py.File(inputpath, 'r') as inputfile:
    with h5py.File(outputpath, 'w') as outputfile:
        manip.fix_materials(
            inputfile, outputfile, xs=options["fix"], layout=options["layout"]
            )

print(f"Successfully fixed '{options['fix']}' for '{inputpath}'")
print(f"The output file is '{outputpath}'")
