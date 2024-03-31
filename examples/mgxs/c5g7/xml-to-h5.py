#!/usr/bin/env python3
"""
Generate a .h5 XS file from the materials.xml
"""
import sys
import xml.etree.ElementTree as ET
import h5py
from antmocdata.mgxs.options import Options
from antmocdata.mgxs.manip import h5, xml


options = Options()

# Reset defaults
options["input"].default = "./materials.xml"
options["output"].default = "./mgxs.h5"

# Parse command line arguments
options.parse(sys.argv[1:])

# Check if we should print a help message
if options("help"):
    options.help()
    sys.exit(1)

xmltree = ET.parse(options("input"))

materials = xml.find_materials(xmltree)

with h5py.File(options("output"), 'w') as outputfile:
    h5.dump_materials(materials, outputfile, layout="named")
