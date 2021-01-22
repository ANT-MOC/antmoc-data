#!/usr/bin/env python3

import sys
from antmoc_mgxs.type_a.options import OptionsTypeA as Options
from antmoc_mgxs.type_a import infilecross


options = Options()

# Parse command line arguments
options.parse(sys.argv[1:])

# Check if we should print a help message
if options["help"]:
    options.help()
    exit(1)

with open(options["sets"], mode="r") as file:
    all_sets = infilecross.find_nuclidesets(file.readlines())

for nuclideset in all_sets.values():
    print("{}\n".format(nuclideset))
    print("nuclides in this set:")
    for nuclide in nuclideset.values():
        print("{}".format(nuclide))
