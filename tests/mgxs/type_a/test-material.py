"""Tests for module generate.

Author: An Wang, USTB (wangan.cs@gmail.com)
Date:   January 23, 2021
"""

from antmocdata.mgxs.type_a import Material


class TestMaterialTypeA:
    def test_compute_xs(self, sample_xml_tree, sample_nuclideset):
        node = sample_xml_tree.getroot()[0]
        material = Material(node)
        material.compute_xs(sample_nuclideset)

        assert material.name == "A"
        assert material.setid == 1
        assert material.info == "Material A"
        assert all([x == y for x, y in zip(material["chi"], [0.5756E+00, 0.2934E+00])])
