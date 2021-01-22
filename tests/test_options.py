"""Tests for module options.

Author: An Wang, USTB (wangan.cs@gmail.com)
Date:   January 24, 2021
"""

import pytest
from antmoc_mgxs.baseoptions import BaseOpt
from antmoc_mgxs.options import Options


class TestOptions():
    def test_help(self):
        """Print the help message."""
        opts = Options()
        opts.help()

        assert True

    def test_add_opt(self):
        """Add an option to the option list."""
        opts = Options()
        opts.add(name="test", default="on", doc="An option for testing")

        assert opts["test"] == "on"

    def test_add_invalid_opt(self):
        """Add an object rather than BaseOpt to the option list."""
        opts = Options()

        with pytest.raises(TypeError):
            opts.add_opt("test")

    def test_set_value(self):
        """Set the value of an option manually."""
        opts = Options()
        opts["help"] = True

        assert opts["help"]

    def test_undefined_option(self):
        """Access an undefined option."""
        opts = Options()

        with pytest.raises(KeyError):
            opts["undefined name"]

        with pytest.raises(KeyError):
            opts["undefined name"] = 1


class TestBaseOpt():
    def test_empty_opt(self):
        """Invalid empty opt."""
        with pytest.raises(ValueError):
            BaseOpt()

    def test_invalid_shortname(self):
        """Short name longer than 1 character."""
        with pytest.raises(ValueError):
            BaseOpt(name="test", shortname="test")
