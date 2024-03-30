"""Class MaterialXML

Author: An Wang, USTB (wangan.cs@gmail.com)
Date:   November 17, 2020
"""

import math
import numpy as np
import re
from .material import Material


class MaterialXML(Material):
    """Material associated with a node in `materials.xml`.

    To generate a Material object, we need an XML node to provide density weights
    and a NuclideSet object to provide cross-section arrays.
    """
    def __init__(self, node=None, nocheck=False):
        """Instantiate a material.

        Parameters
        ----------
        node : xml node
        nocheck: a boolean indicating whether some attributes should be validated
        """
        super().__init__()

        # Unique name
        self.name = node.get("name")

        # Description (optional)
        if "label" in node.attrib:
            self.info = node.get("label")
        else:
            self.info = ""

        # ID of the associated nuclide set
        if "set" in node.attrib:
            self.setid = node.get("set")
        else:
            self.setid = self.name

        # Total density (optional)
        if "density" in node.attrib:
            self.density = node.get("density")
        else:
            self.density = 0.

        # Temperature (optional)
        if "temperature" in node.attrib:
            self.temperature = node.get("temperature")
        else:
            self.temperature = "0K"

        # Weights of nuclides (nuclide ID -> density)
        self.weights = {}
        for subnode in node.findall("nuclide"):
            nuclideid = subnode.get("id")
            nuclideweight = subnode.get("radio")
            self.weights[nuclideid] = nuclideweight

        # Macroscopic cross-sections (optional)
        macronode = node.find("macroscopic")
        if macronode:
            self.data = {}
            for xsnode in macronode:
                x = np.fromstring(xsnode.text, dtype=np.float64, sep=' ')
                if xsnode.tag in Material.xslist:
                    self[xsnode.tag] = x
                if xsnode.tag == "scattering":
                    self["scatter matrix"] = x
            if all(xsname in self.data for xsname in ["nu", "fission"]):
                self["nu-fission"] = self["nu"] * self["fission"]

        # Check and fix attributes
        if not nocheck:
            self.check_and_fix()

    def check_and_fix(self):
        """Check and fix material attributes as needed."""
        self.setid = int(self.setid)
        self.density = float(self.density)

        # Check nuclide ids and density weights
        weights = self.weights
        self.weights = {}
        try:
            for nuclideid, weight in weights.items():
                if isinstance(weight, str):
                    weight = self._fix_float(weight)
                self.add_weight(nuclideid, weight)
        except Exception as exception:
            # Restore weights
            self.weights = weights
            raise exception

    def _fix_float(self, string):
        """Check and fix a floating-point number in a string."""
        # Search for patterns like '1.000-1' or '1.000E-1'
        re_matched = re.match(r"([\+-]?[0-9]\.[0-9]+)[e]?([\+-][0-9]+)", string, re.I)
        if re_matched:
            string = "{}E{}".format(re_matched.group(1), re_matched.group(2))
        return string

    def add_weight(self, nuclideid, weight):
        """Store an id-weight pair to the data array.

        The number of digits of the uid is 4 or 5.
            range 1000 ~ 99999
        This function removes unnecessary digits from the input uid. For example,
            1102301 will be truncated to 11023

        Parameters
        ----------
        nuclideid : uid of a nuclide (int)
        weight : density weight of a nuclide (float)
        """
        real_id = int(nuclideid)
        if math.log10(real_id) > 4:
            real_id = real_id // 100

        if math.log10(real_id) < 3:
            raise ValueError(
                f"Failed to add density weight for material {self.name}:\n"
                f"Nuclide UID {nuclideid} was parsed to be {real_id}, which is invalid."
                )

        # Add the weight to the map
        self.weights[real_id] = float(weight)

    def compute_density(self):
        """Sum up all density weights."""
        weights = [float(self._fix_float(w)) for w in self.weights.values()]
        self.density = sum(weights)

    def __str__(self):
        string = "MaterialXML:\n" \
            f"\tname = {self.name}\n" \
            f"\tset = {self.setid}\n" \
            f"\tinfo = {self.info}\n" \
            f"\tnumber of groups = {self.ngroups}\n"

        string += "\tdensity weights:\n"
        for nuclideid, weight in self.weights.items():
            string += f"\t{nuclideid: <5} = {weight:.5e}\n"

        string += "\tcross-sections:\n"
        for name, array in self.items():
            string += f'\t{name: <14} = {array}\n'

        return string
