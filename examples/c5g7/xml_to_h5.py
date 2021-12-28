#!/usr/bin/env python3

import sys
import h5py
import xml.etree.ElementTree as ET
from antmoc_mgxs.options import Options
from antmoc_mgxs.manip import h5, xml


options = Options()

# Reset defaults
options.opts("input").default = "./materials.xml"
options.opts("output").default = "./mgxs.h5"

# Parse command line arguments
options.parse(sys.argv[1:])

# Check if we should print a help message
if options["help"]:
    options.help()
    exit(1)

xmltree = ET.parse(options["input"])

materials = xml.find_materials(xmltree)

with h5py.File(options["output"], 'w') as outputfile:
    h5.dump_materials(materials, outputfile, layout="named")
