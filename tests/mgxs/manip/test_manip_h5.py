"""Tests for module manip.h5.

Author: An Wang, USTB (wangan.cs@gmail.com)
Date:   January 24, 2021
"""

import pytest
import antmocdata.mgxs.manip.h5 as manip


class TestDataIO:
    def test_load_ngroups(self, sample_h5_input):
        """Load the number of energy groups."""
        ngroups = manip.load_ngroups(sample_h5_input)

        assert ngroups == 6

    def test_dump_ngroups(self, sample_h5_output):
        """Dump the number of energy groups."""
        manip.dump_ngroups(sample_h5_output, ngroups=6)
        ngroups = manip.load_ngroups(sample_h5_output)

        assert ngroups == 6

    def test_undefined_layout(self, sample_h5_input):
        """Undefined material data file layout."""
        with pytest.raises(ValueError):
            manip.load_materials(sample_h5_input, layout="unknown")

    def test_load_materials(self, sample_h5_input):
        """Load materials from a file."""
        manip.load_materials(sample_h5_input)

        assert True

    def test_dump_materials(self, sample_material, sample_h5_output):
        """Dump materials to a file."""
        materials = {sample_material.name: sample_material}

        manip.dump_materials(materials=materials, file=sample_h5_output)

        assert True

    def test_convert_layout(self, sample_h5_input, sample_h5_output):
        """Conversion between 'named' and 'compact' layouts."""
        manip.convert_layout(
            inputfile=sample_h5_input,
            outputfile=sample_h5_output,
            layout="named"
            )

        named_materials = manip.load_materials(sample_h5_input, layout="named")
        compact_materials = manip.load_materials(sample_h5_output, layout="compact")

        for name in named_materials:
            assert named_materials[name] == compact_materials[name]


class TestFixMaterials:
    def test_fix_scatter_matrix(self, sample_h5_input, sample_h5_output):
        """Fix scatter matrices for materials."""
        manip.fix_materials(
            inputfile=sample_h5_input,
            outputfile=sample_h5_output,
            xs="sigma_s"
            )

        assert True

    def test_fix_sigma_total(self, sample_h5_input, sample_h5_output):
        """Fix total cross-sections for materials."""
        manip.fix_materials(
            inputfile=sample_h5_input,
            outputfile=sample_h5_output,
            xs="sigma_t"
            )

        assert True


class TestCheckMaterials:
    def test_check_negative_xs(self, sample_h5_input):
        """Check negative values in xs arrays."""
        assert manip.check_negative_xs(sample_h5_input) is True

    def test_check_sigma_t(self, sample_h5_input):
        """Check 'total' and 'transport'."""
        assert manip.check_sigma_t(sample_h5_input) is False
