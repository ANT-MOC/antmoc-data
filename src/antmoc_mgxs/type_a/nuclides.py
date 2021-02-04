"""Nuclide representation

Classes:
    Nuclide
    NuclideSet

Author: An Wang, USTB (wangan.cs@gmail.com)
Date:   January 22, 2021
"""

import numpy as np


class Nuclide:
    """A nuclide with cross-sections.

    See infilecross._parse_nuclide(...) for how to parse a Nuclide from strings.

    Examples
    --------
    URANIUM 235 with 6 energy groups
    >>> Cr50 = Nuclide(name="Chromium", number=24, mass=50, ngroups=6)

    >>> print(Cr50.name, Cr50.number, Cr50.mass, Cr50.uid())
    CHROMIUM 24 50 24050
    """
    def __init__(self, name="", number=0, mass=0, ngroups=0):
        """Construct a Nuclide object.

        Parameters
        ----------
        name : element name
        number : atomic number
        mass : atomic mass
        ngroups : number of energy groups
        """
        # Element name
        self.name = name.upper()

        # Atomic number
        self.number = number

        # Atomic mass
        self.mass = mass

        # Number of energy groups
        self.ngroups = ngroups

        # Cross-sections
        self.data = {}

    def __getitem__(self, xsname):
        if xsname not in self.data and xsname == "nu-fission":
            # Compute nu-fission as needed
            self.data[xsname] = np.array(self.data["nu"]) * np.array(self.data["fission"])
        return self.data[xsname]

    def __setitem__(self, xsname, array):
        self.data[xsname] = array

    def uid(self):
        """Return the ID of this nuclide.

        For example,
            - the ID of URANIUM-235 is 92235 = 92 * 1000 + 235
            - the ID of SODIUM-23 is 11023 = 11 * 1000 + 23
        """
        return self.number * 1000 + self.mass

    def __str__(self):
        string = "Nuclide:\n" \
            "\tname = {}\n" \
            "\tuid = {}\n" \
            "\tnumber = {}\n" \
            "\tmass = {}\n" \
            "\tnumber of groups = {}\n".format(
                self.name, self.uid(), self.number, self.mass, self.ngroups)

        for xsname in self.data:
            string += "\t{: <14} = {}\n".format(xsname, self.data[xsname])

        return string


class NuclideSet:
    """A NuclideSet includes many nuclides which share the same Chi array.

    See infilecross.parse_nuclideset(...) for how to parse a NuclideSet from strings.

    Each set contains a number of nuclides and an array of chi for all of
    the nuclides. A set may be mapped to multiple materials.

    Examples
    --------
    Instantiate an empty NuclideSet
    >>> nuclideset = NuclideSet()

    """
    def __init__(self, uid=0, nnuclides=0, ngroups=0):
        """Instantiate a NuclideSet."""
        # NuclideSet ID
        self.uid = int(uid)

        # Number of nuclides
        self.nnuclides = nnuclides

        # Number of energy groups
        self.ngroups = ngroups

        # Chi
        self.chi = np.array([])

        # Nuclides (nuclide uid -> nuclide object)
        self.nuclides = {}

    def __getitem__(self, nuclideid):
        return self.nuclides[nuclideid]

    def keys(self):
        """Return keys of the nuclide dictionary."""
        return self.nuclides.keys()

    def values(self):
        """Return values of the nuclide dictionary."""
        return self.nuclides.values()

    def add_nuclide(self, nuclide):
        """Add a nuclide to the set."""
        self.nuclides[nuclide.uid()] = nuclide

    def size(self):
        """Number of nuclides in the set."""
        if self.nnuclides != len(self.nuclides):
            raise ValueError(
                f"Mismatched number of nuclides: {self.nnuclides} required "
                f"but {len(self.nuclides)} found.\n"
                f"{str(self)}"
                )
        return len(self.nuclides)

    def __str__(self):
        """Return the set as a string."""
        return f"Nuclide Set:\n" \
               f"\tuid = {self.uid}\n" \
               f"\tnumber of groups = {self.ngroups}\n" \
               f"\tnumber of nuclides = {self.nnuclides}\n" \
               f"\tnuclide list length = {len(self.nuclides)}\n" \
               f"\tchi = {self.chi}\n" \
               f"\tnuclide ids = {self.keys()}"


if __name__ == "__main__":
    import doctest
    doctest.testmod()
