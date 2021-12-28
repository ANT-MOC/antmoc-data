"""H5 data manipulation utilities.

Functions:
    load_ngroups(...)
    dump_ngroups(...)
    load_xsindices(...)
    dump_xsindices(...)
    load_materials(...)
    dump_materials(...)
    convert_layout(...)
    fix_materials(...)
    check_sigma_t(...)
    check_negative_xs(...)

Author: An Wang, USTB (wangan.cs@gmail.com)
Date:   January 24, 2021
"""

import warnings
import numpy as np
from ..material import Material


def iterate_materials(file, layout="named"):
    """Return a generator for iterating materials in a file."""
    ngroups = load_ngroups(file)

    for group in file["material"].values():
        material = Material(ngroups=ngroups)
        material.load(group=group, layout=layout)
        yield material


def load_ngroups(file):
    """Read the number of energy groups from an H5 file.

    Parameters
    ----------
    file : H5 file object
    """
    return file.attrs["# groups"]


def dump_ngroups(file, ngroups):
    """Store the number of energy groups to an H5 file.

    Parameters
    ----------
    file : H5 file object
    """
    file.attrs["# groups"] = np.int64(ngroups)


def load_xsindices(file):
    """Read the XS indices from an H5 file.

    This is for compressed/compact layout.
    Only cross-section names listed in Material.xslist will be searched among
    the H5 group attributes.
    """
    materialgroup = file["material"]
    xsindices = {}
    for xsname in Material.xslist:
        if f"idx {xsname}" in materialgroup.attrs:
            xsindices[xsname] = materialgroup.attrs[f"idx {xsname}"]

    return xsindices


def dump_xsindices(file, xsindices):
    """Store the XS indices to an H5 file.

    This is for compressed/compact layout.
    """
    if "material" in file.keys():
        materialgroup = file["material"]
    else:
        materialgroup = file.create_group("material")

    for xsname, xsindex in xsindices.items():
        materialgroup.attrs[f"idx {xsname}"] = np.int8(xsindex)


def load_materials(file, layout="named"):
    """Load all materials from an H5 file object.

    This function is memory-consuming. It would be better to process materials
    one-by-one. See fix_scatter_matrices(...).

    Parameters
    ----------
    file : H5 file object
    layout : data layout, either 'name' or 'compressed'/'compact'

    Return
    ------
    A dictionary of materials
    """
    # Read the number of energy groups
    ngroups = load_ngroups(file)

    # Open the top group for reading
    h5_top_group = file["material"]

    materials = {}

    for name in h5_top_group:
        materials[name] = Material(ngroups=ngroups)
        materials[name].load(group=h5_top_group[name], layout=layout)

    return materials


def dump_materials(materials, file, layout="named"):
    """Dump all materials to an H5 file object.

    Parameters
    ----------
    materials : a dictionary of materials
    file : H5 file object
    layout : data layout, either 'name' or 'compressed'/'compact'
    """
    if not materials:
        warnings.warn("Empty material dictionary", Warning)
        return

    # Check the number of energy groups
    first_key = next(iter(materials))
    ngroups = materials[first_key].ngroups
    for material in materials.values():
        if material.ngroups != ngroups:
            raise ValueError(
                f"Mismatched number of energy groups:\n"
                f"# groups in material {first_key} = {ngroups}\n"
                f"# groups in material {material.name} = {material.ngroups}"
                )

    # Create a top level group as needed
    if "material" in file:
        h5_top_group = file["material"]
    else:
        h5_top_group = file.create_group("material")

    dump_ngroups(file, ngroups)
    for material in materials.values():
        material.dump(parent=h5_top_group, layout=layout)


def convert_layout(inputfile, outputfile, layout="named"):
    """Convert H5 layout from 'named' to 'compact' or vice versa."""
    # Read and write the number of energy groups
    ngroups = load_ngroups(inputfile)
    dump_ngroups(outputfile, ngroups)

    # Open the top-level group for output
    outgroup = outputfile.create_group("material")

    # Set the output layout, read or write extra attributes
    if layout.lower() in ["named", "openmoc"]:
        outlayout = "compact"
        dump_xsindices(outputfile, Material.xsindices)
    elif layout.lower() in ["compact", "compressed"]:
        outlayout = "named"
        Material.xsindices = load_xsindices(inputfile)
    else:
        raise ValueError(f"Undefined H5 file layout {layout}")

    materials = iterate_materials(inputfile, layout)
    for material in materials:
        material.dump(parent=outgroup, layout=outlayout)


def fix_materials(inputfile, outputfile, xs="sigma_s", layout="named"):
    """Fix the scatter matrix for all materials.

    Parameters
    ----------
    inputfile : H5 file object for reading materials
    outputfile : H5 file object for storing fixed materials
    layout : data layout, either 'name' or 'compressed'/'compact'
    xs : string indicating which array to be fixed
        sigma_s, sigma_t
    """
    if xs.lower() not in ["sigma_s", "sigma_t"]:
        raise ValueError(f"No such routine to fix '{xs}'")

    # Read and write the number of energy groups
    ngroups = load_ngroups(inputfile)
    dump_ngroups(outputfile, ngroups)

    # Open the top-level group for output
    out_top_group = outputfile.create_group("material")

    materials = iterate_materials(inputfile, layout)
    for material in materials:
        if xs.lower() == "sigma_s":
            material.fix_scatter_matrix()
        elif xs.lower() == "sigma_t":
            material.fix_sigma_total()

        material.dump(parent=out_top_group, layout=layout)


def check_sigma_t(file, layout="named", tolerance=1e-15):
    """Check 'total' or 'transport'.

    Check whether each of the values is no less than the sum of 'absorption'
    and 'scatter matrix'.

    Parameters
    ----------
    file : an H5 file object
    layout : material data layout type
    tolerance : tolerance for floating-point comparison

    Return
    ------
    True if a sigma_t exists and is good, False otherwise
    """
    materials = iterate_materials(file, layout)

    xsnames = ["total", "transport"]
    missing_sigma_t = []
    is_good = True

    for material in materials:
        ngroups = material.ngroups
        expected = material.build_sigma_total()

        if all(xs not in material.keys() for xs in xsnames):
            # Check whether the material have a sigma_t
            missing_sigma_t.append(material.name)
            continue

        results = {}
        for xs in xsnames:
            if xs in material.keys():
                # Compare each of the values
                result = [
                    (i + 1, f"{material[xs][i]:.5E}", f"{expected[i]:.5E}")
                    for i in range(ngroups) if material[xs][i] < expected[i] - 1e-13
                    ]
                # If there are any negative values, keep it for reporting
                if result:
                    results[xs] = result

        if results:
            is_good = False
            print(f"Total XS smaller than expected found in material {material.name}.\n"
                  "Results are formatted to (group, actual, expected).")
            for xs, array in results.items():
                print(f"In array '{xs}':\n{array}")
            print()

    if missing_sigma_t:
        is_good = False
        print(f"Materials missing a sigma_t:\n{missing_sigma_t}")

    return is_good


def check_negative_xs(file, layout="named"):
    """Check negative values in xs data file.

    Return
    ------
    True if there is no negative value, False otherwise.
    """
    materials = iterate_materials(file, layout)
    is_good = True

    for material in materials:
        ngroups = material.ngroups
        results = {}
        for xs, array in material.items():
            # Find negative values in the scatter matrix
            if xs.find("scatter") < 0:
                result = [
                    (i+1, f"{array[i]:.5E}")
                    for i in range(ngroups) if array[i] < .0
                    ]
            else:
                result = [
                    (i // ngroups + 1, i % ngroups + 1, f"{array[i]:.5E}")
                    for i in range(ngroups * ngroups) if array[i] < .0
                    ]
            # If there are any negative values, keep it for reporting
            if result:
                results[xs] = result

        if results:
            is_good = False
            print(f"Negative values found in material {material.name}.\n"
                  "Results for the scatter are formatted to (group, group, value).\n"
                  "Results for the rest are formatted to (group, value).")
            for xs, array in results.items():
                print(f"In array '{xs}':\n{array}")
            print()

    return is_good


if __name__ == "__main__":
    import doctest
    doctest.testmod()
