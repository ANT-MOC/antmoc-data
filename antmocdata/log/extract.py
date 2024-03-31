#!/usr/bin/env python3

"""A package for getting records from antmoc log files.

Authors: An Wang, USTB (wangan.cs@gmail.com)

Date: 2020/11/15

"""

import csv
import datetime
import textwrap
import timeit

import antmocdata.log.data
import antmocdata.log.fields


class TinyExtractor(object):
    """A class to extract records from a LogDB object.

    Records will be written into a csv file.

    Arguments
    ---------
    logdb : LogDB
        A database object of antmoc log
    specs : list of strings
        Field specs to be queried
    sortby :
        Sort the results by a key
    delimiter : string
        Separator of record fields, used to input arrays
    output : string
        File to save the results
    truncate : bool
        File mode to open the output file
        True for "w", False for "a"
    summary : bool
        Print only a summary for record rather than print them out

    >>> logdb = antmocdata.log.data.LogDB()

    >>> extractor = TinyExtractor(logdb = logdb)

    >>> extractor.setup(antmocdata.log.options.LogOptions())

    """

    def __init__(self, logdb, specs = None, sortby = "", delimiter = " | ", output = "antmoc-records.csv", truncate = False, summary = False):
        self.logdb      = logdb
        self.specs      = specs
        self.sortby     = sortby
        self.delimiter  = delimiter
        self.output     = output
        self.truncate   = truncate
        self.summary    = summary


    def setup(self, options):
        """Initialize extractor attributes with an options object."""
        self.specs      = options["specs"].value
        self.sortby     = options["sortby"].value
        self.delimiter  = options["delimiter"].value
        self.output     = options["output"].value
        self.truncate   = options["truncate"].value
        self.summary    = options["summary"].value


    def extract(self):
        """Extract records from the LogDB object and print a report.
        This method results in a csv file.
        """

        # Timer start
        t_start = timeit.default_timer()

        # Print the head and arguments
        print("")
        print("{:=^{}}".format("BEGIN", 80))
        print("Current time:\n\t{}\n".format(datetime.datetime.now()))
        print("Output file:\n\t{}\n".format(self.output))

        # Extract records in parallel
        record_list = self.logdb.query(specs = self.specs, sortby = self.sortby)

        # Expand field patterns for output
        specs = antmocdata.log.fields.expand_specs(self.specs)

        mode = "w" if self.truncate else "a"

        # Output
        with open(self.output, mode = mode, newline = "") as csvfile:

            # Create a writer
            csvwriter = csv.writer(csvfile)

            # Header
            labels = [str(x) for x in specs]

            # Print the header to stdout & file
            if not self.summary:
                print("Records:\n{}\n".format(self.delimiter.join(labels)))
            csvwriter.writerow(labels)

            logfields = antmocdata.log.fields.LogFields()

            for record in record_list:
                # Format the record lines
                fmt_line = []
                for i in range(len(record[1])):
                    v     = record[1][i]
                    dtype = logfields[specs[i].name].dtype
                    fmt   = logfields[specs[i].name].fmt
                    fmt_line.append(fmt.format(dtype(v)) if v is not None else "")

                # Print records to stdout & file
                if not self.summary:
                    print(self.delimiter.join(fmt_line))
                csvwriter.writerow(fmt_line)

        # Print number of records which has broken fields
        if not self.summary:
            print("")
            print("Records with broken fields:\n")

            for record in record_list:
                if record[2]:
                    brokens = ", ".join(record[2])
                    wrapped_text = textwrap.indent(textwrap.fill(brokens, 80), "\t")
                    print("{}:\n{}".format(record[0]["File"], wrapped_text))

        count_broken = sum([1 for record in record_list if record[2]])

        # Timer stop
        t_stop = timeit.default_timer()

        # Report
        print("")
        print("{:=^{}}".format("Extractor report", 80))
        print("Number of records = {}".format(len(record_list)))
        print("Number of records with broken fields = {}".format(count_broken))
        print("Time = {:.3f} s".format(t_stop - t_start))
        print("Extracted records have been written to '{}'".format(self.output))
        print("{:=^{}}".format("END", 80))
        print("")

if __name__ == "__main__":
    import doctest
    doctest.testmod()
