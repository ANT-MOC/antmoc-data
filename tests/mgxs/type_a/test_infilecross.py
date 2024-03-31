"""Tests for module infilecross.

Author: An Wang, USTB (wangan.cs@gmail.com)
Date:   January 22, 2021
"""

import pytest
from antmocdata.mgxs.type_a import infilecross


class TestParseNuclideName:
    def test_1(self):
        """Name and mass separated by a hyphen."""
        strings = [
            "OXYGEN-16",
            "oxygen-16",
            "0OXYGEN-16",
            " \t 5801606  0  3  0OXYGEN-16  ",
        ]

        for string in strings:
            assert infilecross.parse_nuclide_name(string) == ('OXYGEN', 8, 16)

    def test_2(self):
        """Compact form."""
        strings = [
            "PU239"
            "Pu239.PF"
            "  7751023906   0   3   6Pu239.PF                ",
            " \t 7751023906   0   3   6Pu239.PF \t ",
        ]

        for string in strings:
            assert infilecross.parse_nuclide_name(string) == ('PU', 94, 239)

    def test_3(self):
        """Undefined name pattern."""
        with pytest.raises(ValueError):
            infilecross.parse_nuclide_name("U")
            infilecross.parse_nuclide_name("U-")

    def test_4(self):
        """Undefined element."""
        with pytest.raises(KeyError):
            infilecross.parse_nuclide_name("EEZO-0")


class TestParseNuclideSetId:
    """Tests for robustness."""
    def test_1(self):
        strings = [
            "$Some string 1 7SETs 2SET \t",
            "$Some string 2SET",
            "\t \t$hello 2SET",
            "$something set2"
        ]

        for string in strings:
            assert infilecross.parse_nuclideset_id(string) == 2

    def test_2(self):
        with pytest.raises(ValueError):
            infilecross.parse_nuclideset_id("Some string 1 7SETs 2SET")

    def test_3(self):
        with pytest.raises(ValueError):
            infilecross.parse_nuclideset_id("$Some string 1 7SETs SET")

    def test_4(self):
        with pytest.raises(ValueError):
            infilecross.parse_nuclideset_id("$Some string 1 7SETs")


class TestParseChi:
    def test_1(self):
        string = "0.57564402E+00  0.29341474E+00  0.12731624E+00  0.30919870E-02"
        oracle = [0.57564402E+00, 0.29341474E+00, 0.12731624E+00, 0.30919870E-02]

        assert infilecross.parse_chi(string) == oracle

    def test_2(self):
        with pytest.raises(ValueError):
            infilecross.parse_chi("")


class TestParseCountNuclidesGroups:
    """Tests for robustness."""
    def test_1(self):
        strings = [
            " \t 2 30 6 5 0 0",
            "2  30   6 5 0 0 \t ",
            "2  30 \t 6 5 0 0",
        ]

        for string in strings:
            assert infilecross.parse_count_nuclides_groups(string) == (30, 6)

    def test_2(self):
        with pytest.raises(ValueError):
            infilecross.parse_nuclideset_id("2 30 6")

    def test_3(self):
        with pytest.raises(ValueError):
            infilecross.parse_nuclideset_id("2 0 6 5 0 0")

    def test_4(self):
        with pytest.raises(ValueError):
            infilecross.parse_nuclideset_id("2 30 0 5 0 0")


class TestParseXSArrays:
    def test_1(self):
        strings = [
            "0.1505E-02  0.6758E-05  0.1733E+01  0.2000E+01  0.6758E-05  0.0E+00",
            "0.2867E-03  0.0000E+00  0.2946E+01  0.0000E+00  0.0000E+00  0.0E+00"
        ]

        oracle = {
            "absorption": [0.1505E-02, 0.2867E-03],
            "fission": [0.6758E-05, 0],
            "transport": [0.1733E+01, 0.2946E+01],
            "nu": [0.2E+01, 0E+00]
        }

        results = infilecross.parse_xs_arrays(strings)

        assert results == oracle

    def test_2(self):
        strings = [
            "0.1505E-02  0.6758E-05"
            "0.2867E-03  0.0000E+00"
        ]

        xsindices = {
            "absorption": 0,
            "fission": 1,
            "transport": 2,
            "nu": 3
        }

        with pytest.raises(ValueError):
            infilecross.parse_xs_arrays(strings, xsindices)


class TestParseScatterMatrix:
    def test_1(self):
        strings = [
            "0.2054E+01  0.5554E+00",
            "0.0000E+00  0.3412E+01"
        ]

        oracle = [0.2054E+01, 0.5554E+00, 0.0000E+00, 0.3412E+01]

        results = infilecross.parse_scatter_matrix(strings)

        assert results == oracle

    def test_2(self):
        strings = [
            "0.2054E+01  0.5554E+00 0.1E+01",
            "0.0000E+00  0.3412E+01"
        ]

        with pytest.raises(ValueError):
            infilecross.parse_scatter_matrix(strings)


class TestParseNuclideSet:
    def test_1(self):
        """Nuclide set with 2 nuclides and 2 energy groups."""
        plaintext = """$SOMESTRING 1  7SETs 1SET
            2  2  2  5   0   0
            0.5756E+00  0.2934E+00
            -----
            -----
            2511102302   0   3   6SODIUM-23
            -----
            -----
            -----
            0.15E-02  0.67E-05  0.17E+01  0.20E+01  0.67E-05
            0.28E-03  0.00E+00  0.29E+01  0.00E+00  0.00E+00
            0.20E+01  0.55E+00
            0.00E+00  0.34E+01
            4311402802   0   3   6SILICON-28
            -----
            -----
            -----
            0.15E-02  0.67E-05  0.17E+01  0.20E+01  0.67E-05
            0.28E-03  0.00E+00  0.29E+01  0.00E+00  0.00E+00
            0.20E+01  0.55E+00
            0.00E+00  0.34E+01
            """
        strings = plaintext.split("\n")
        setmarks = {
            "header": 1,
            "counts": 2,
            "chi": 3,
            "nuclides": 6
        }
        nuclidemarks = {
            "header": 1,
            "xs": 5
        }

        nuclideset = infilecross.parse_nuclideset(
            strings=strings,
            setmarks=setmarks,
            nuclidemarks=nuclidemarks
        )

        assert nuclideset.uid == 1
        assert nuclideset.nnuclides == 2
        assert nuclideset.ngroups == 2
        assert all([x == y for x, y in zip(nuclideset.chi, [0.5756E+00, 0.2934E+00])])

        nuclide_ids = nuclideset.nuclides.keys()
        assert 11023 in nuclide_ids
        assert 14028 in nuclide_ids

    def test_2(self):
        """Nuclide set with 1 nuclides and 1 energy groups."""
        plaintext = """$SOMESTRING 1  7SETs 1SET
            2  1  1  5   0   0
            0.57564402E+00  0.29341474E+00
            -----
            2511102302   0   3   6SODIUM-23
            -----
            0.15E-02  0.67E-05  0.17E+01  0.20E+01  0.67E-05
            0.20E+01
            0.00E+00
            """
        strings = plaintext.split("\n")
        setmarks = {
            "header": 1,
            "counts": 2,
            "chi": 3,
            "nuclides": 5
        }
        nuclidemarks = {
            "header": 1,
            "xs": 3
        }

        nuclideset = infilecross.parse_nuclideset(
            strings=strings,
            setmarks=setmarks,
            nuclidemarks=nuclidemarks
        )

        assert nuclideset.uid == 1
        assert nuclideset.nnuclides == 1
        assert nuclideset.ngroups == 1

        nuclide_ids = nuclideset.nuclides.keys()
        assert 11023 in nuclide_ids
