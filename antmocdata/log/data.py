#!/usr/bin/env python3

"""Log data representation for antmoc.

Classes: LogFile, LogDB

Authors: An Wang, USTB (wangan.cs@gmail.com)

Date: 2020/11/16

"""

import collections
import datetime
import hashlib
import json
import multiprocessing
import pathlib
import re
from antmocdata.log.fields import LogFields, expand_specs
from antmocdata.log.options import LogOptions


class LogFile(object):
    """Log file representation.

    A log file contains many key-value pairs which stored in an ordered
    dictionacy. Each value in the object is supposed to have a type and
    the type will be checked during construction.

    key   : field name
    value : field value

    To format the values, please use dtype of corresponding Field object.
    See package antmocdata.log.fields for more details.

    Parameters
    ----------
    path : string
        Path to the log file
    format : string
        File format, "txt" or "json" for now

    Examples
    --------

    Instantiate a log file object
    >>> logfile = LogFile(path = "log.txt")

    Query a specified field
    >>> print(logfile["Azims"])

    Iterate over items
    >>> for field, value in logfile.items():

    Instantiate a log file with JSON serializer
    >>> logfile = LogFile(path = "log.txt", format = "json")

    Query a specified field
    >>> print(logfile["Azims"])

    Save data to a new file
    >>> logfile.save("log.json")

    Compute the hash for a LogFile object
    >>> print(logfile.hash())

    """

    def __init__(self, path = None, format = "txt"):
        """Parse a log file with a specified file format."""

        self.path = path
        self.format = format

        if path is not None:
            self.data = LogFileSerializer(format).load(path)
        else:
            self.data = collections.OrderedDict()

    def __getitem__(self, name):
        """Return a field value."""
        if name in self.data.keys():
            return self.data[name]
        else:
            raise KeyError("Field '{}' was not found".format(name))

    def __setitem__(self, name, value):
        """Modify existing field value."""
        if name in self.data.keys():
            self.data[name] = value
        else:
            raise KeyError("Field '{}' was not found".format(name))

    def __str__(self):
        return json.dumps(self.data, indent = 2)

    def hash(self):
        """Hash a logfile to get a unique id.
        It is no need to sort the data because it is an OrderedDict.
        """
        return hashlib.md5(json.dumps(self.data, indent=2).encode("utf-8")).hexdigest()

    def save(self, path, mode = "x"):
        """Save data to a new file."""
        with open(path, mode = mode) as file:
            json.dump(obj = self.data, fp = file, indent = 2)

    def save_in_place(self):
        """Save data to the original file.
        Be careful that this method will truncate the file.
        """
        self.save(path = self.path, mode = "w")

    def items(self):
        return self.data.items()

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def findall(self, specs):
        """Search the log file for a list of field specs.

        During this method, each spec will be expanded to concrete field names.

        For each concrete field name,
        and field value will be returned.

        Parameters
        ----------
        specs : list
            List of field specs, see antmocdata.log.fields.FieldSpec for more details.

        Returns
        -------
        ([field values], [fields not found]) :
            A tuple of two lists
        """

        # Expand perl regex
        specs = expand_specs(specs)

        field_values = []
        not_found = []

        for spec in specs:
            # Use the predicate for filtering.
            # The predicate will handle value type.
            if spec.pred(self[spec.name]):
                field_values.append(self[spec.name])
                if self[spec.name] is None:
                    not_found.append(spec.name)
            else:
                return None, None

        return field_values, not_found


class LogDB(object):
    """Log database representation.

    A LogDB object holds a dictionary of (file path, LogFile object) pairs.
    The key, file path, refers to the full path to the log file. If a LogFile
    object is accessed in the dict-like way, the database object will read
    the file and create the LogFile object as needed.

    key   : full path to file
    value : LogFile object

    Parameters
    ----------
    options : LogOptions
        Options for log analysis

    Public attributes
    -----------------
    nprocs : int (default = 1)
        Number of available cpus

    cache : boolean (default = False)
        Indicating whether log files should be cached

    fileformat : string (default = "txt")
        Default file format

    Private attributes
    ------------------
    _filepatterns : list
        List of file name patterns

    _files : dict, filename -> (path object, format)
        Dictionary of pathlib paths and formats

    _logfiles : dict, file path -> logfile object
        Dictionary of logfiles

    Examples
    --------
    Instantiate an database object (a log file will be read only if it is accessed)
    >>> logdb = LogDB(nprocs = 4, filenames = ["./**/*.log", "./**/*.txt"])

    Instantiate an empty database object and set it up using options
    >>> logdb = LogDB()

    >>> logdb.setup(LogOptions())
    LogDB: added 1 file pattern(s) and 0 path(s)

    Query JobId and any field ended with 'Time'
    #>>> print(logdb.query(["JobId", ".*Time"]))

    """

    def __init__(self, nprocs = 1, filenames = [], fileformat = "txt", cache = False):

        self.nprocs     = nprocs
        self.cache      = cache
        self.fileformat = fileformat

        # Patterns
        self._filepatterns = filenames

        # Paths
        self._files = collections.OrderedDict()

        # Cached log files
        self._logfiles = multiprocessing.Manager().dict()

    def __getitem__(self, path_format):
        """Return a LogFile object by full path.

        Parameters
        ----------
        path_format: tuple (path, format)
            File path and file format
            The format can be omitted, and the default will be taken
        """
        # Unpack the argument
        try:
            path, format = path_format
        except:
            path = path_format
            format = self.fileformat

        if not self.cache:
            return LogFile(path, format = format)
        else:
            return self.cache_file(path, format = format)

    def setup(self, options):
        """Setup the DB with options.
        This method takes options "nprocs", "cache", and "filenames".
        """
        if isinstance(options, LogOptions):
            self.nprocs     = int(options["nprocs"].value)
            self.cache      = options["cache"].value
            self.fileformat = options["fileformat"].value
            self.add_paths(options["filenames"].value, self.fileformat)
        else:
            raise TypeError("The options passed to LogDB is of a wrong type")

    def reset(self):
        """Reset attributes."""
        #FIXME: is the memory managed elegantly?
        self._filepatterns = []
        self._files = collections.OrderedDict()
        self._logfiles = multiprocessing.Manager().dict()

    def has_file(self, path):
        """Check if a file path exists."""
        return path.resolve() in self._files.keys()

    def add_paths(self, patterns, format = None):
        """Add file paths matching given patterns to the DB."""
        if isinstance(patterns, str):
            patterns = [patterns]

        # Set to the default
        if format is None:
            format = self.fileformat

        # Counting files
        count = len(self._files)

        # Find new patterns
        new_patterns = []
        for pattern in patterns:
            if not pattern:
                continue

            # Cache patterns and file paths
            if pattern not in self._filepatterns:
                new_patterns.append(pattern)
                for f in [x for x in pathlib.Path().glob(pattern) if x.is_file()]:
                    if not self.has_file(f):
                        self._files[f.resolve()] = (f, format)

        # Incrementally add new patterns and update the file list
        self._filepatterns.extend(new_patterns)

        print("LogDB: added {} file pattern(s) and {} path(s)".format(len(new_patterns), len(self._files) - count))

    def remove_paths(self, patterns):
        """Remove file paths matching given patterns."""
        pass

    def _dump_to_file(self, path, directory):
        """Save a single log file to a directory.
        path : string, full path to the file
        directory : PosixPath, path to save log files

        Returns
        -------
        True : dumped
        False : skipped
        """
        # Get a cached log file, or create it
        logfile = self[path]

        filepath = directory / "{}.json".format(logfile.hash())

        if filepath.exists():
            return False
        else:
            logfile.save(filepath.resolve(), mode = "x")
            return True

    def save(self, directory):
        """Save log files to a directory.
        Each file is in JSON format and will be named with a hash number.

        Parameters
        ----------
        directory : string
            Path to save log files. The directory will be created if it doesn't exists.
        """
        path = pathlib.Path(directory)
        if path.exists():
            # Check if the path leads to a directory
            if not path.is_dir():
                raise OSError(f"Path '{directory}' is not a directory")
        else:
            # Create a new directory
            path.mkdir()

        # Generate arguments for starmap
        arg_paths = self._files.keys()
        arg_dirs  = [path for x in self._files.values()]

        with multiprocessing.Pool(processes = self.nprocs) as pool:
            are_dumped = pool.starmap(self._dump_to_file, zip(arg_paths, arg_dirs))

        n_dumped  = sum([1 for x in are_dumped if x])
        n_skipped = len(are_dumped) - n_dumped

        print(f"LogDB: skipped {n_skipped} file(s), saved {n_dumped} file(s) to '{path.resolve()}'")

    def cache_file(self, path, format):
        """Read a single log file immediatelly.

        Parameters
        ----------
        path : string
            Full path to the file path
        format : string
            File format
        """
        if path in self._logfiles.keys():
            return self._logfiles[path]
        else:
            logfile = LogFile(path, format = format)
            self._logfiles[path] = logfile
            return logfile

    def cache_all(self):
        """Read all log files immediatelly."""
        # Counting files
        count = -len(self._logfiles)

        # Generate arguments for starmap
        arg_paths = self._files.keys()
        arg_fmts  = [x[1] for x in self._files.values()]

        with multiprocessing.Pool(processes = self.nprocs) as pool:
            pool.starmap(self.cache_file, zip(arg_paths, arg_fmts))

        count += len(self._logfiles)

        print("LogDB: {} file(s) newly cached, {} in total".format(count, len(self._logfiles)))

    def query_file(self, path, format, specs):
        """Query a single log file with field specs.

        Parameters
        ----------
        path : string
            Full path to the file
        format : string
            File format
        specs :  list
            List of field specs to be queried

        Returns
        -------
        (logfile, [field values], [field not found]) :
            A tuple of results
        """

        # Get a cached log file, or create it
        logfile = self[path, format]

        # Values and broken fields
        values, broken_fields = logfile.findall(specs)

        if values is None:
            # Return None to indicate this file was excluded
            return None
        else:
            return (logfile, values, broken_fields)


    def query(self, specs, sortby = ""):
        """Query all log files with field specs.

        Parameters
        ----------
        specs :  list
            List of field specs to be queried
        sortby : string, optional (default: '')
            A field used to sort the records

        Returns
        -------
        [ (logfile, [field values], [field not found]) ] :
            A list of tuple. Each tuple contains results returned by a single log file.
        """

        # Reporting
        print("LogDB: querying with {} processes".format(self.nprocs))
        print("LogDB: file name patterns =\n\t{}".format("\n\t".join(self._filepatterns)))
        print("LogDB: field specs =\n\t{}".format(", ".join(specs)))

        # Generate arguments for starmap
        arg_paths = self._files.keys()
        arg_fmts  = [x[1] for x in self._files.values()]
        arg_specs = [specs for x in range(len(self._files))]

        with multiprocessing.Pool(processes = self.nprocs) as pool:
            records = pool.starmap(
                self.query_file, zip(arg_paths, arg_fmts, arg_specs)
            )

        # Remove None values
        records = [x for x in records if x]

        print("LogDB: current cached files = {}".format(len(self._logfiles)))

        # Sort by the specified key. Before that, a value must be converted to
        # the proper type, otherwise floating-point numbers will not be handled
        # properly.
        logfields = LogFields()
        if sortby:
            records.sort( key = lambda record : logfields[sortby].dtype(record[0][sortby]) )

        return records


class LogFileSerializer(object):
    """A serializer for reading and writing log fiels.

    Parameters
    ----------
    format : string
        File format

    Examples
    --------

    >>> serializer = LogFileSerializer(format = "txt")

    >>> serializer = LogFileSerializer(format = "json")

    """

    def __new__(cls, format = "txt"):
        if format == "txt":
            return LogFileSerializerTXT()
        elif format == "json":
            return LogFileSerializerJSON()
        else:
            raise ValueError("Unrecoganized file format of LogFileSerializer: {}".format(format))


class LogFileSerializerTXT(object):
    """A TXT serializer for log files.

    Examples
    --------

    >>> serializer = LogFileSerializerTXT()

    >>> print(serializer.load("log.txt"))

    """

    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(LogFileSerializerTXT, cls).__new__(cls)
        return cls.instance

    def load(self, path):
        """Load a file and parse it to return a dictionary."""

        # Initialize a PosixPath
        path = pathlib.Path(path)
        stat = path.stat()

        # Initialize a dictionary for underlying data
        data = collections.OrderedDict([
            ("JobId", ""),
            ("File",            str(path)),
            ("FileTimeStamp",   str(datetime.datetime.fromtimestamp(stat.st_mtime))),
            ("FileSize",        "{:.1f}".format(stat.st_size / 1000)), # KB
        ])

        # Extract jobid from the file name
        id_matched = re.match(r"^([0-9]+)-", path.name, re.I)

        if id_matched:
            data["JobId"] = id_matched.group(1)

        # Extract each field from the file
        f = open(path, mode = "r")
        file_content = f.read()
        f.close()

        logfields = LogFields()
        for field in logfields.values():
            try:
                # Try all possible patterns until the first match
                pattern_found = False
                for pattern in field.patterns:
                    re_matched = re.findall(pattern, file_content, re.I)
                    if re_matched:
                        data[field.name] = re_matched[-1]

                        # Try to convert the string to field dtype.
                        # We don't really want this value being stored in the
                        # object because it will prevent us to filter log files
                        # by perl regex.
                        field.dtype(re_matched[-1])

                        pattern_found = True
                        break
                if field.patterns and not pattern_found:
                    raise TypeError()
            except:
                # Set the value to empty if failed to parse a field
                data[field.name] = None

        return data


class LogFileSerializerJSON(object):
    """A JSON serializer for log files."""

    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(LogFileSerializerJSON, cls).__new__(cls)
        return cls.instance

    def load(self, path):
        with open(path, mode = "r") as file:
            data = json.load(file)

        return data
