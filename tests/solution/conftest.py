"""Fixtures for testing module convert"""

import pytest
import pathlib


@pytest.fixture(scope="function")
def sample_vtu_file_rx1():
    """A vtu file for testing."""
    # Get the path of the sample file
    path = pathlib.Path(__file__).parent.absolute() / "rx1.vtu"

    # Yield a file object and do some clean after testing
    file = open(str(path), "r")
    yield file
    file.close()


@pytest.fixture(scope="function")
def sample_vtu_file_rx2():
    """A vtu file for testing."""
    # Get the path of the sample file
    path = pathlib.Path(__file__).parent.absolute() / "rx2.vtu"

    # Yield a file object and do some clean after testing
    file = open(str(path), "r")
    yield file
    file.close()
