#!/usr/bin/env python3

import sys
from antmocdata.mgxs.type_a import Options
from antmocdata.mgxs.type_a import infilecross


options = Options()

# Parse command line arguments
options.parse(sys.argv[1:])

# Check if we should print a help message
if options("help"):
    options.help()
    exit(1)

with open(options("sets"), mode="r") as file:
    all_sets = infilecross.find_nuclidesets(file.readlines())

for nuclideset in all_sets.values():
    print(f"{nuclideset}\n")
    print("nuclides in this set:")
    for nuclide in nuclideset.values():
        print(nuclide)
