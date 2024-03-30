#!/usr/bin/env python3

import sys
import xml.etree.ElementTree as ET
from antmocdata.mgxs.type_a import Options
from antmocdata.mgxs.type_a import infilecross, generate_mgxs_h5


options = Options()

# Additional options
options.add(name="fix-scatter", dtype=bool, doc="Fix scatter matrices")

# Reset defaults
options["output"].default = "./mgxs.h5"

# Parse command line arguments
options.parse(sys.argv[1:])

# Check if we should print a help message
if options("help"):
    options.help()
    exit(1)

# Read densities
xmltree = ET.parse(options("materials"))

# Set up marks for nuclide set data sections.
# This could be commented out to use the default marks.
setmarks = {
    "header": 1,
    "counts": 2,
    "chi": 3,
    "nuclides": 9
}

# Set up marks for nuclide data sections.
# This could be commented out to use the default marks.
nuclidemarks = {
    "header": 1,
    "xs": 12
}

# Read nuclide sets
with open(options("sets"), "r") as file:
    allsets = infilecross.find_nuclidesets(
        strings=file.readlines(),
        setmarks=setmarks,
        nuclidemarks=nuclidemarks
        )

# Generate an H5 file for materials
generate_mgxs_h5(
    file=options("output"),
    xmltree=xmltree,
    nuclidesets=allsets,
    fixscatter=options("fix-scatter")
    )

print("Successfully generated file {}".format(options("output")))
