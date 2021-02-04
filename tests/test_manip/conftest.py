"""Fixtures for testing module manip"""

import pytest
import h5py
import pathlib


@pytest.fixture(scope="function")
def sample_h5_input():
    """An H5 file path for testing."""
    # Get the path of the sample file
    path = pathlib.Path(__file__).parent.absolute() / "mgxs.h5"

    # Yield an H5 file object and do some clean after testing
    h5_input = h5py.File(str(path), 'r')
    yield h5_input
    h5_input.close()


@pytest.fixture(scope="function")
def sample_h5_output():
    """An H5 file path for testing."""
    # Get the path of the output file
    path = pathlib.Path(__file__).parent.absolute() / "mgxs.out.h5"

    # Yield an H5 file object and do some clean after testing
    h5_output = h5py.File(str(path), 'w')
    h5_output.close()

    h5_output = h5py.File(str(path), 'r+')
    yield h5_output
    h5_output.close()
    path.unlink()
