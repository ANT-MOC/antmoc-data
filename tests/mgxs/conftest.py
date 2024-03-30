"""Common fixtures"""

import pytest
import numpy as np
import xml.etree.ElementTree as ET
from antmocdata.mgxs import Material


@pytest.fixture(scope="function")
def sample_material():
    data = {
        "absorption": np.array([1.0E+00, 5.0E-01]),
        "fission": np.array([1.0E+00, 5.0E-01]),
        "nu-fission": np.array([1.0E-01, 5.0E-02]),
        "chi": np.array([1.0E-01, 5.0E-02]),
        "transport": np.array([1.0E-01, 5.0E-02]),
        "scatter matrix": np.array([1.0E-01, 5.0E-01, 0.0E-00, 1.0E-01]),
    }
    return Material(name="A", ngroups=2, data=data)


@pytest.fixture
def sample_xml_tree():
    return ET.ElementTree(ET.fromstring(
        """<?xml version="1.0" encoding="utf-8"?>
        <MATERIALS>
            <material name="A" set="1" density="0." temperature="600K" label="Material A">
                <nuclide id="1102301" radio="1E+0"/>
                <nuclide id="1402801" radio="1E-1"/>
            </material>
            <material name="B" set="1" density="0." temperature="600K" label="Material B">
                <nuclide id="1102302" radio="2.1618e-2"/>
                <nuclide id="1402802" radio="2.9073e-4"/>
                <nuclide id="6012"    radio="1.7693e-5"/>
            </material>
        </MATERIALS>
        """
        ))
