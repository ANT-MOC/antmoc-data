"""Material Type A

Class: MaterialTypeA

Author: An Wang, USTB (wangan.cs@gmail.com)
Date:   November 17, 2020
"""

import warnings
import numpy as np
from ..materialxml import MaterialXML


class MaterialTypeA(MaterialXML):
    # Redefine the list since there is no cross-section 'total'
    xslist = [
        "absorption",
        "fission",
        "transport",
        "nu-fission",
        "chi",
        "scatter matrix",
    ]

    def __init__(self, node=None, nocheck=False):
        super().__init__(node=node, nocheck=nocheck)

    def compute_xs(self, nuclideset):
        """Compute cross-sections according to nuclides and nuclide density weights.

        Parameters
        ----------
        nuclideset : a NuclideSet object.
        """
        # Reset the number of energy groups
        self.ngroups = nuclideset.ngroups

        # Reset all of the data arrays
        for xsname in MaterialTypeA.xslist:
            if xsname.find('scatter') >= 0:
                self[xsname] = np.zeros(
                    (self.ngroups * self.ngroups,), dtype=np.float64
                )
            else:
                self[xsname] = np.zeros(self.ngroups, dtype=np.float64)

        # Loop over all density weights and associated nuclides
        for nuclideid, weight in self.weights.items():

            # Skip zero-weight nuclide
            if weight == .0:
                warnings.warn(
                    f"Nuclide {nuclideid} skipped for material {self.name} "
                    f"since it has zero weight"
                    )
                continue

            # Check if the nuclide id could be fount in the set
            if nuclideid not in nuclideset.keys():
                raise ValueError(
                    f"Failed to find nuclide {nuclideid} in set {nuclideset.uid} "
                    f"for material {self.name}.\n"
                    f"details of the nuclide set:\n{nuclideset}"
                    )

            nuclide = nuclideset[nuclideid]

            # Sum up cross-sections over nuclides
            for xsname in MaterialTypeA.xslist:
                if xsname == "chi":
                    # Skip Chi array since it is defined for all nuclides in a set.
                    continue
                else:
                    self[xsname] += np.array(nuclide[xsname]) * weight

        # Chi, defined for all nuclides in a set
        self['chi'] = nuclideset.chi
