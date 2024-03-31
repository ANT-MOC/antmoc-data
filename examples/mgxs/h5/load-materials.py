#!/usr/bin/env python3
"""
Load and print material files
"""
import sys
import h5py
from antmocdata.mgxs.options import Options
import antmocdata.mgxs.manip.h5 as manip


options = Options()

# Reset default values
options["input"].default = "./mgxs.h5"

# Parse command line arguments
options.parse(sys.argv[1:])

# Check if we should print a help message
if options("help"):
    options.help()
    sys.exit(1)

with h5py.File(options("input"), 'r') as file:
    materials = manip.load_materials(
        file=file, layout=options("layout"))

# Print materials
for material in materials.values():
    print(material)
