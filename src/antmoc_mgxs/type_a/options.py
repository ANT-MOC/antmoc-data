"""Class OptionsTypeA

Author: An Wang, USTB (wangan.cs@gmail.com)
Date:   November 16, 2020

"""

from ..options import Options


class OptionsTypeA(Options):
    """Options for module type_a."""

    def __init__(self):
        super().__init__()

        # Append available options
        self.add(name="sets", shortname="s", default="./infilecross", valspec="FILE",
                 doc="Nuclide sets file (plain text)")
        self.add(name="materials", shortname="m", default="./materials.xml", valspec="FILE",
                 doc="material information and densities (xml)")

        # Remove some options
        self.remove("input")
