"""Tests for loading .vtu files"""

import pytest
from antmocdata.solution import load_vtu


class TestLoadVtu:
    def test_load_vtu(self, sample_vtu_file_rx1):
        """Load a .vtu file"""
        rx1 = load_vtu(sample_vtu_file_rx1, ["^Avg Fission RX$"])
        fiss = rx1["Avg Fission RX"]

        assert fiss.shape == (45, 51, 51)
