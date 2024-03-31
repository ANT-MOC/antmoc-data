"""Class Options

Author: An Wang, USTB (wangan.cs@gmail.com)
Date:   November 16, 2020

"""

from baseopt import BaseOption, BaseOptions


class Options(BaseOptions):
    """Basic options.

    This class can parse command line options. Each of the BaseOpt object can
    be accessed by either its full name or short name.

    Command line arguments are supposed to be passed to method parse(...).
        import sys
        options = Options()
        options.parse(sys.argv[1:])

    Examples
    --------

    Instantiate Options
    >>> options = Options()

    >>> isinstance(options, Options)
    True

    Get option value of "h"
    >>> print(options("h"))
    False

    Add an option to the object
    >>> options.add(name="test")

    >>> options["test"].value = "hello world"

    Print the option of "test"
    >>> print(options("test"))
    hello world

    """

    def __init__(self):
        super().__init__()

        # Append available options
        self.add(name="help", shortname="h", dtype=bool, doc="Show this message")
        self.add(name="input", shortname="i", default="./a.inp", valspec="FILE",
                 doc="input filename")
        self.add(name="output", shortname="o", default="./a.out", valspec="FILE",
                 doc="output filename")
        self.add(name="layout", default="named",
                 doc="data layout in the H5 file ('named' or 'compact')")


if __name__ == "__main__":
    import doctest
    doctest.testmod()
