"""Tests for module manip.xml

Author: An Wang, USTB (wangan.cs@gmail.com)
Date:   January 23, 2021
"""

import pytest
import warnings
import xml.etree.ElementTree as ET
import antmoc_mgxs.manip.xml as manip
from antmoc_mgxs.materialxml import MaterialXML as Material


class TestReadMaterials:
    def test_find_materials(self, sample_xml_tree):
        """Read objects from an XML tree."""
        materials = manip.find_materials(sample_xml_tree)

        material_a = materials["A"]
        assert material_a.name == "A"
        assert material_a.setid == 1
        assert material_a.info == "Material A"
        assert material_a.weights[11023] == 1E+0

        material_b = materials["B"]
        assert material_b.name == "B"
        assert material_b.setid == 1
        assert material_b.info == "Material B"
        assert material_b.weights[14028] == 2.9073e-4

    def test_read_single_material(self, sample_xml_tree):
        """Read a single object."""
        node = sample_xml_tree.getroot()[0]
        material = Material(node)

        assert material.name == "A"
        assert material.setid == 1
        assert material.density == 0.
        assert material.info == "Material A"
        assert material.weights[14028] == 1E-1

        # Print the material
        print(material)

    def test_invalid_nuclide_id(self):
        """Invalid nuclide id."""
        tree = ET.ElementTree(ET.fromstring(
            """<?xml version="1.0" encoding="utf-8"?>
            <ROOT>
                <material name="A"> <nuclide id="110" radio="2.1618e-2"/> </material>
            </ROOT>
            """
            ))
        node = tree.getroot()[0]

        with pytest.raises(ValueError):
            Material(node)


class TestModifyXML:
    def test_reset_all_densities(self, sample_xml_tree):
        """Read the xml tree and reset densities for materials."""
        xmltree = manip.reset_all_densities(sample_xml_tree)
        node = xmltree.getroot()[0]

        assert float(node.get("density")) == 1.1E+00

    def test_replace_nuclide_ids(self, sample_xml_tree):
        """Replace nuclide ids."""
        warnings.simplefilter("error")

        idmap = {
            1102301: 10,
            1402801: 11,
            1102302: 10,
            1402802: 11,
            6012: 12,
        }

        xmltree = manip.replace_nuclide_ids(sample_xml_tree, idmap)
        nuclide = xmltree.getroot()[0][0]
        assert int(nuclide.get("id")) == 10

    def test_reset_nuclideset_ids(self, sample_xml_tree):
        """Reset nuclideset ids."""
        warnings.simplefilter("error")

        idmap = {
            "A": 111,
            "B": 222,
        }

        xmltree = manip.reset_nuclideset_ids(sample_xml_tree, idmap)

        node = xmltree.getroot()[0]
        assert int(node.get("set")) == 111
        node = xmltree.getroot()[1]
        assert int(node.get("set")) == 222
