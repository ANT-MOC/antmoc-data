"""Functions to manipulate materials.xml

Functions:
    find_materials(...)
    reset_all_densities(...)
    reset_nuclideset_ids(...)
    replace_nuclide_ids(...)
    add_nuclide_id_suffixes(...)

Author: An Wang, USTB (wangan.cs@gmail.com)
Date:   January 22, 2021
"""

import warnings
from ..materialxml import MaterialXML


def find_materials(xmltree):
    """Read materials from an XML tree.

    To use this function, first you should parse the XML file or string to get a tree.
        tree = xml.etree.ElementTree.parse(xml_file)
        or
        tree = xml.etree.ElementTree.fromstring(xml_string)

    Then, pass the tree to this function to get an array of material objects.
        find_materials(tree)

    Parameters
    ----------
    xmltree : XML element tree.

    Return
    ------
    A dictionary of material objects indexed by material names.

    Examples
    --------
    Each material object is represented as an XML node.
    A simple material with 2 nuclides:

        <?xml version="1.0" encoding="utf-8"?>
        <MATERIALS>
            <material name="A" set="1" density="0." temperature="600K" label="Material A">
                <nuclide id="1102301" radio="2.1618e-2"/>
                <nuclide id="6012"    radio="1.7693e-5"/>
            </material>
        </MATERIALS>
    """
    root = xmltree.getroot()

    # All material definitions read from the XML tree.
    materials = {}

    # Loop over elements
    for node_mat in root.findall("material"):
        material = MaterialXML(node=node_mat)
        materials[material.name] = material

    return materials


def reset_all_densities(xmltree):
    """Read materials and compute densities by summing up density weights."""
    # Loop over materials and reset the density for each of them
    root = xmltree.getroot()
    for node in root.iter("material"):
        material = MaterialXML(node=node, nocheck=True)
        material.compute_density()
        node.set("density", f"{material.density:.6e}")

    return xmltree


def replace_nuclide_ids(xmltree, idmap):
    """Replace nuclide ids using a customized dictionary.
    The dictionary consists of 'id -> newid' pairs.

    Parameters
    ----------
    xmltree : an xml tree
    idmap : a dictionary
    """
    idmap = {str(key): str(value) for key, value in idmap.items()}
    root = xmltree.getroot()

    unchanged_ids = set()
    missing_ids = set()

    for node in root.iter("material"):
        for nuclide in node.iter("nuclide"):
            nuclideid = nuclide.get("id")
            if nuclideid in idmap:
                nuclide.set("id", idmap[nuclideid])
            elif nuclideid in idmap.values():
                # If the id is not a key but is a value in the dictionary, skip it
                unchanged_ids.add(nuclideid)
            else:
                missing_ids.add(nuclideid)

    if unchanged_ids:
        warnings.warn(
            f"Some nuclide ids were not found in dictionary keys but found in values:\n"
            f"{unchanged_ids}",
            stacklevel=2)

    if missing_ids:
        warnings.warn(
            f"Some nuclide ids were not found in the dictionary:\n"
            f"{missing_ids}",
            stacklevel=2)

    return xmltree


def reset_nuclideset_ids(xmltree, idmap):
    """Reset nuclideset ids using a customized dictionary.
    The dictionary consists of 'material name -> newid' pairs.

    Parameters
    ----------
    xmltree : an xml tree
    idmap : a dictionary
    """
    idmap = {str(key): str(value) for key, value in idmap.items()}

    reset_names = set()
    unchanged_names = set()

    root = xmltree.getroot()
    for node in root.iter("material"):
        name = node.get("name")
        if name in idmap:
            node.set("set", idmap[name])
            reset_names.add(name)
        else:
            unchanged_names.add(name)
            warnings.warn(
                f"Missing material name {name} in nuclideset id dictionary:\n"
                f"{idmap}")

    if reset_names:
        print(f"Nuclide ids have been reset for the following materials:\n"
              f"{reset_names}")

    if unchanged_names:
        print(f"Nuclide ids of some materials were left unchanged:\n"
              f"{unchanged_names}")

    return xmltree


def add_nuclide_id_suffixes(xmltree):
    """Add nuclide set id as suffixes to nuclide ids."""
    root = xmltree.getroot()
    for node in root.iter("material"):
        # Look for an valid set id
        for attr in ["set", "name"]:
            setid = node.get(attr)
            if setid:
                break
        setid = int(setid)

        # Check the length of the set id
        if setid // 100 != 0:
            warnings.warn(f"Nuclide set id {setid} may be too long")

        # Append the set id to the nuclide id
        for nuclide in node.iter("nuclide"):
            nuclideid = nuclide.get("id")
            nuclide.set("id", f"{nuclideid}{setid:02}")

    return xmltree
