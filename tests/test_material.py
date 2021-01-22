"""Tests for module material.

Author: An Wang, USTB (wangan.cs@gmail.com)
Date:   January 24, 2021
"""

import pytest
import numpy as np


class TestMaterial:
    def test_undefined_xsname(self, sample_material):
        """Undefined cross-section name."""
        material = sample_material

        with pytest.raises(KeyError):
            material["unknown"] = np.array([.0, .0])

    def test_print_material(self, sample_material):
        """Print a material."""
        print(sample_material)

        assert True

    def test_equal(self, sample_material):
        """Operator '=='"""
        material_a = sample_material
        material_b = material_a.copy()

        assert material_a == material_b

    def test_not_equal(self, sample_material):
        """Operator '!='"""
        material_a = sample_material
        material_b = material_a.copy()

        material_b["absorption"] += 1E-12

        assert material_a != material_b
