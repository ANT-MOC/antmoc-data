"""Functions to generate materials

Functions:
    setup_materials(...)
    generate_mgxs_h5(...)
    reset_all_densities(...)

Author: An Wang, USTB (wangan.cs@gmail.com)
Date:   January 22, 2021
"""

import warnings
import h5py
import numpy as np
from .material import MaterialTypeA


def setup_materials(xmltree, nuclidesets):
    """Read material definitions from an XML tree and compute cross-sections for them.

    Parameters
    ----------
    xmltree : XML element tree.
    nuclidesets : a dictionary of NuclideSet object indexed by set id.

    Return
    ------
    A dictionary of Material objects indexed by material names.
    """
    root = xmltree.getroot()
    materials = {}

    # Loop over materials
    for node in root.findall("material"):
        # Instantiate a material
        material = MaterialTypeA(node=node)
        materials[material.name] = material

        if material.setid not in nuclidesets.keys():
            warnings.warn(
                f"Failed to find nuclide set {material.setid} for material {material.name}.\n"
                f"Available nuclide sets = {nuclidesets.keys()}",
                stacklevel=2
                )
            continue

        material.compute_xs(nuclidesets[material.setid])

    return materials


def generate_mgxs_h5(file, xmltree, nuclidesets, fixscatter=False):
    """Read materials, compute cross-sections for them, and dump them to an H5 file.

    Parameters
    ----------
    See function setup_materials(...)
    """
    # Generate materials.
    materials = setup_materials(xmltree, nuclidesets)

    # Dump materials to an H5 file.
    with h5py.File(file, "w") as h5_file:
        # Create the top-level group.
        h5_top = h5_file.create_group("material")

        # Dump each material.
        for material in materials.values():
            ngroups = material.ngroups

            # Fix diagonal elements of the scatter matrix as needed
            if fixscatter:
                material.fix_scatter_matrix()

            material.dump(h5_top)

        # Write the number of groups to the file as an top-level attribute.
        h5_file.attrs["# groups"] = np.int64(ngroups)
