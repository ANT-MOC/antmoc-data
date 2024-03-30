"""Fixtures"""

import pytest
from antmocmgxs.type_a import infilecross


@pytest.fixture
def sample_nuclideset():
    plaintext = """$SOMESTRING 1  7SETs 1SET
        2  2  2  5   0   0
        0.5756E+00  0.2934E+00
        2511102302   0   3   6SODIUM-23
        1.0E+0  1.0E+0  1.0E+0  1.0E+0  1.0E+0  1.0E+0
        1.0E+0  1.0E+0  1.0E+0  1.0E+0  1.0E+0  1.0E+0
        1.0E+0  1.0E+0
        1.0E+0  1.0E+0
        4311402802   0   3   6SILICON-28
        1.0E-1  1.0E-1  1.0E-1  1.0E-1  1.0E-1  1.0E-1
        1.0E-1  1.0E-1  1.0E-1  1.0E-1  1.0E-1  1.0E-1
        1.0E-1  1.0E-1
        1.0E-1  1.0E-1
        """
    strings = plaintext.split("\n")
    setmarks = {
        "header": 1,
        "counts": 2,
        "chi": 3,
        "nuclides": 4
    }
    nuclidemarks = {"header": 1, "xs": 2}

    return infilecross.parse_nuclideset(
        strings=strings,
        setmarks=setmarks,
        nuclidemarks=nuclidemarks
    )
