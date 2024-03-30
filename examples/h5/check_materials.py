#!/usr/bin/env python3
"""
Check the total XS, find negative XS records
"""
import sys
import h5py
from antmoc_mgxs.options import Options
import antmoc_mgxs.manip.h5 as manip


options = Options()

# Reset default values
options["input"].default = "./mgxs.h5"

# Remove unnecessary options
options.remove("output")

# Parse command line arguments
options.parse(sys.argv[1:])

# Check if we should print a help message
if options("help"):
    options.help()
    sys.exit(1)

with h5py.File(options("input"), 'r') as inputfile:
    manip.check_sigma_t(inputfile, layout=options("layout"))
    manip.check_negative_xs(inputfile, layout=options("layout"))
