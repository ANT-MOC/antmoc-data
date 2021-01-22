#!/usr/bin/env python3

import sys
import json
import xml.etree.ElementTree as ET
import antmoc_mgxs.manip.xml as manip
from antmoc_mgxs.options import Options


options = Options()

# Additional options
options.add(name="fix-density", isbool=True, doc="Reset material density")
options.add(name="fix-ids", isbool=True, doc="Fix nuclide ids")
options.add(name="nuclideset-ids", default=None,
            doc="A json file for resetting nuclideset ids")
options.add(name="nuclide-ids", default=None,
            doc="A json file for replacing nuclide ids")

# Reset defaults
options.opts("input").default = "materials.xml"
options.opts("output").default = "materials.fixed.xml"

# Parse command line arguments
options.parse(sys.argv[1:])

# Check if we should print a help message
if options["help"]:
    options.help()
    exit(1)

xmltree = ET.parse(options["input"])

# Reset density for materials
if options["fix-density"]:
    xmltree = manip.reset_all_densities(xmltree)
    print("Successfully fixed material densities")

# Reset nuclideset ids using an user-provided dictionary
filename = options["nuclideset-ids"]
if filename:
    with open(filename, "r") as json_file:
        nuclideset_id_map = json.load(json_file)
        xmltree = manip.reset_nuclideset_ids(xmltree, nuclideset_id_map)
    print("Successfully fixed nuclideset ids with file {}".format(filename))

# Replace nuclide ids using an user-provided dictionary
filename = options["nuclide-ids"]
if filename:
    with open(filename, "r") as json_file:
        nuclide_id_map = json.load(json_file)
        xmltree = manip.replace_nuclide_ids(xmltree, nuclide_id_map)
    print("Successfully fixed nuclide ids with file {}".format(filename))

# Fix nuclide ids by adding suffixes
if options["fix-ids"]:
    xmltree = manip.add_nuclide_id_suffixes(xmltree)
    print("Successfully added nuclide set ids as suffixes to nuclide ids")

xmltree.write(options["o"])
print("File '{}' generated".format(options["o"]))
