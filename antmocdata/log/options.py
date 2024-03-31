#!/usr/bin/env python3

"""Class for antmocdata.log options.

Classes: LogOptions

Authors: An Wang, USTB (wangan.cs@gmail.com)

Date: 2020/11/16

"""

import multiprocessing
from baseopt import BaseOption, BaseOptions
from .fields import help_fields


class LogOptions(BaseOptions):
    """Singleton class Options for antmocdata.log.

    This class can parse command line options. Each of the BaseOption object can
    be accessed by either its full name or short name.

    Command line arguments are supposed to be passed to method parse(...).
    e.g.
        import sys
        options = LogOptions()
        options.parse(sys.argv[1:])

    Examples
    --------

    Instantiate LogOptions
    >>> options = LogOptions()

    >>> isinstance(options, LogOptions)
    True

    Get option value of "h"
    >>> print(options["h"].value)
    False

    Get option value of "output"
    >>> print(options["output"].value)
    antmoc-records.csv

    Add an option to the object
    >>> options.add_options([ BaseOption(name="test") ])

    >>> options["test"].value = "hello world"

    Print the option value of "test"
    >>> print(options["test"].value)
    hello world

    """

    # Uncomment this block to make it an singleton
    #instance = None

    #def __new__(cls):
    #    if cls.instance is None:
    #        cls.instance = super(LogOptions, cls).__new__(cls)
    #    return cls.instance

    def __init__(self):
        super().__init__()

        # Append available options
        self.add_options([
            BaseOption(name="help",        shortname="h", dtype=bool, doc="Show this message"),

            BaseOption(name="help-fields", shortname="",  dtype=bool, doc="Show a list of available fields"),

            BaseOption(name="nprocs",      shortname="n", default=multiprocessing.cpu_count(),
                doc="Number of processes to run"),

            BaseOption(name="cache",       dtype=bool,
                doc="Cache log files in memory. Not to cache files will save memory but read files everytime they are needed."),

            BaseOption(name="filenames",   shortname="f", default=["log/**/*.log"],  delimiter=" ", valspec="GLOB1[ GLOB2 ...]",
                doc="Log filename patterns"),

            BaseOption(name="fileformat",  shortname="x", default="txt", valspec="STR",
                doc="Log file format, which may used as the default format"),

            BaseOption(name="specs",       shortname="e", default=[".*"], delimiter=" ", valspec="SPEC1[ SPEC2 ...]",
                doc="Field specs used to extract log records. A spec is a string with three parts: field name, op, and value. The op and value are used to filter log files."),

            BaseOption(name="output",      shortname="o", default="antmoc-records.csv", valspec="FILE",
                doc="CSV file to store extracted records"),

            BaseOption(name="truncate",    shortname="",  dtype=bool,
                doc="Truncate the output file"),

            BaseOption(name="sortby",      shortname="",  valspec="FIELD",
                doc="Sort the results by a field"),

            BaseOption(name="delimiter",   shortname="",  default=" | ",
                doc="delimiterarator between field values used for formatted printing"),

            BaseOption(name="savedb",      valspec="DIR",
                doc="Save the log file database in json to a directory"),

            BaseOption(name="summary",     shortname="",  dtype=bool,
                doc="Print a summary for the query rather than list the results"),
        ])

    def help_fields(self):
        return help_fields()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
