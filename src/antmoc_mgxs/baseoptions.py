"""Representation of options.

Classes:
    BaseOpt
    BaseOptions

Author: An Wang, USTB (wangan.cs@gmail.com)
Date:   November 17, 2020
"""

import getopt
import collections


class BaseOpt:
    """A single option representation.

    The minimal requirement to instantiate BaseOpt is a name, which can be
    either the full name or short name.

    Parameters
    ----------
    name: string, optional (default = "")
        Full name, which will be prefixed by '--' to be the longarg

    shortname: string, optional (default = "")
        Short name, which will be prefixed by '-' to be the shortarg

    default: object, optional (default = None)
        Default argument

    sep: string, optional (default = "")
        Separator for splitting value string

    isbool: bool, optional (default = False)
        Boolean indicating whether the option accept an argument

    valspec: string, optional (default = "")
        Docstring for option value specification

    doc: string, optional (default = "")
        Docstring for option itself

    Examples
    --------

    Create an option with only its full name
    >>> opt = BaseOpt(name = "help")

    Create an option with only its short name
    >>> opt = BaseOpt(shortname = "h")

    An option without a name is not allowed
    >>> opt = BaseOpt()
    Traceback (most recent call last):
        ...
    ValueError: A BaseOpt object must have a name or a shortname

    Create an option which has no argument
    >>> opt = BaseOpt(name = "help", shortname = "h", isbool = True)

    Show name
    >>> opt.name
    'help'

    Show short name
    >>> opt.shortname
    'h'

    Show command line argument name
    >>> opt.longarg
    '--help'

    Show command line argument name
    >>> opt.shortarg
    '-h'

    >>> opt.value
    False

    Set the value to something and check it
    >>> opt.value = "hello world"

    >>> opt.value
    True

    Create an option which has an argument
    >>> opt = BaseOpt(name = "output", shortname = "o", default = "out.txt", sep = " ")

    Show value, which is the same as its default
    >>> opt.value
    'out.txt'

    Set the option value to a string, which will be splitted later
    >>> opt.value = "out1.txt out2.txt"

    >>> opt.value
    ['out1.txt', 'out2.txt']

    Set the option value to a list
    >>> opt.value = ["out3.txt", "out4.txt"]

    >>> opt.value
    ['out3.txt', 'out4.txt']

    Show longarg for getopt
    >>> opt.get_longarg()
    'output='

    Show shorarg for getopt
    >>> opt.get_shortarg()
    'o:'

    Check if an arg matches the option args
    >>> opt.match_arg("--output")
    True

    >>> opt.match_arg("-o")
    True

    """

    def __init__(self, name="", shortname="", default=None, sep="",
                 isbool=False, valspec="", doc=""):

        super().__setattr__('_attrs', collections.OrderedDict([
            ("name",       name),
            ("shortname",  shortname),
            ("longarg",    "--{}".format(name) if name else ""),
            ("shortarg",   "-{}".format(shortname) if shortname else ""),
            ("default",    default),
            ("value",      None),
            ("sep",        sep),
            ("isbool",     isbool),
            ("valspec",    valspec),
            ("doc",        doc),
            ]
        ))

        if not self.name and not self.shortname:
            raise ValueError("A BaseOpt object must have a name or a shortname")

        if len(self.shortname) > 1:
            raise ValueError("Shortname of a BaseOpt object must a single character")

    def __setattr__(self, name, value):
        if name in ["value", "default"]:
            if isinstance(value, str) and self.sep:
                # Split the value into a list
                self._attrs[name] = [i.strip() for i in value.split(self.sep)]
            else:
                # Supposed to be a list
                self._attrs[name] = value
        else:
            self._attrs[name] = value

    def __getattr__(self, name):
        """Return an attribute.

        A bool option will always return its value/default as a boolean.
        Other options will return its default if its value is not set.
        """
        if name not in self._attrs:
            raise AttributeError("Attribute '{}' not found in BaseOpt object".format(name))

        if name in ["value", "default"]:
            if self._attrs["isbool"]:
                return self._attrs[name] is not None
            if self._attrs[name] is None:
                # Return the default value if the value is not set
                return self._attrs["default"]
        # Otherwise, just return the attribute
        return self._attrs[name]

    def names(self):
        """Return all possible nonempty names."""
        tup_names = ()
        for name in [self.name, self.shortname, self.longarg, self.shortarg]:
            if name:
                tup_names += (name,)
        return tup_names

    def get_longarg(self):
        """Return the long argument name in terms of getopt."""
        return '{}{}'.format(self.name, "" if self.isbool else "=")

    def get_shortarg(self):
        """Return the short argument name in terms of getopt."""
        return '{}{}'.format(self.shortname, "" if self.isbool else ":")

    def match_arg(self, arg):
        """Check if a name matches argument representations of this opt object."""
        return arg in [self.longarg, self.shortarg]

    def __str__(self):
        return str(self._attrs.items())


class BaseOptions:
    """Options representation.

    This class can parse command line options using getopt and store them as
    BaseOpt objects. Each of the BaseOpt object can be accessed by either its
    full name or short name.

    To use this class, please define a subclass and call the method add_opts()
    in its constructor to add a list of BaseOpt objects.

    Examples
    --------
    >>> options = BaseOptions()

    Add an option
    >>> options.add(name="help", default=False, isbool=True)

    >>> options["help"]
    False

    Modify the value
    >>> options["help"] = True

    >>> options["help"]
    True

    Modify other attributes of an option
    >>> options.opts("help").default = True

    >>> options.opts("help").default
    True
    """

    def __init__(self):
        self.data = collections.OrderedDict()

    def __getitem__(self, name):
        """Return the value of the specified BaseOpt object."""
        return self.opts(name).value

    def __setitem__(self, name, value):
        """Set the value of an option."""
        self.opts(name).value = value

    def __str__(self):
        return str(self.data.items())

    def _find_key(self, name):
        """Find a key for the specified name."""
        for names in self.data.keys():
            if name in names:
                return names
        raise KeyError("Option '{}' not found. Available options = {}".format(name, self))

    def opts(self, name):
        """Return a BaseOpt object."""
        key = self._find_key(name)
        return self.data[key]

    def add(self, name="", shortname="", default=None, sep="",
            isbool=False, valspec="", doc=""):
        """Add a BaseOpt object to the option list."""
        self.add_opt(
            BaseOpt(
                name=name,
                shortname=shortname,
                default=default,
                sep=sep,
                isbool=isbool,
                valspec=valspec,
                doc=doc
                )
            )

    def add_opt(self, opt):
        """Add a BaseOpt object to the option list.

        Parameters
        ----------
        opt : a BaseOpt object
        """
        if isinstance(opt, BaseOpt):
            self.data[opt.names()] = opt
        else:
            raise TypeError("opt must be a BaseOpt object")

    def add_opts(self, opts):
        """Extract keys to generate a dictionary for BaseOpt objects.

        Parameters
        ----------
        opts : a list of BaseOpt objects
        """
        for opt in opts:
            self.add_opt(opt)

    def remove(self, name):
        """Remove a BaseOpt object from the option list."""
        key = self._find_key(name)
        del self.data[key]

    def keys(self):
        """Return an option name list."""
        return self.data.keys()

    def values(self):
        """Return BaseOpt object list."""
        return self.data.values()

    def get_shortargs(self):
        """Return all available short argument names."""
        return [i.get_shortarg() for i in self.values() if i.get_shortarg()]

    def get_longargs(self):
        """Return all available long argument names."""
        return [i.get_longarg() for i in self.values() if i.get_longarg()]

    def parse(self, argv):
        """Call getopt to parse command line arguments."""

        args, extra = getopt.getopt(argv, "".join(self.get_shortargs()), self.get_longargs())

        for argname, argvalue in args:
            for opt in self.values():
                if opt.match_arg(argname):
                    opt.value = True if opt.isbool else argvalue

    def help(self, wspec=25, wline=90, indent="  "):
        """Return a help message.

        Parameters
        ----------
        wspec : int, optional
            Maximum width for option spec (without option doc).
            A new line will be started for the option doc if a spec is too long.
        wline : int, optional
            Maximum width for lines. Any string exceeded a line will be wrapped.
            The width is no less than 70.
        indent : string, optional
            Indentation for each line.
        """

        wspec = max(0, wspec)
        wline = max(70, wline)

        doc_opts = []

        # Indentation for option doc lines
        docind = "{}{: ^{}}".format(indent, "", wspec)

        for opt in self.values():
            # Get argument names
            argnames = [i for i in [opt.shortarg, opt.longarg] if i]
            msg = "{}{}".format(indent, " | ".join(argnames))

            # Get value spec
            if not opt.isbool and opt.valspec:
                msg += " {}".format(opt.valspec)

            # Extra whitespace between spec and doc
            msg += "  "

            if opt.doc:
                if len(msg) > wspec + len(indent):
                    # Start new lines if the option spec is too long
                    msg += "\n"
                else:
                    # otherwise just set the alignment
                    msg = "{: <{}}".format(msg, len(docind))

                # Get option docstring
                msg += opt.doc

                # Get default value
                if opt.default is not None:
                    if isinstance(opt.default, str):
                        fmt_def = "\"{}\""
                    else:
                        fmt_def = "{}"
                    msg += "\n(def = {})".format(fmt_def).format(opt.default)

                # Wrap the whole string as needed.
                # A wrapped line must be prefixed with the proper indentation, which
                # is defined by the variable docind. The length of a new line is counted
                # everytime the indentation is inserted.
                i_start = 0  # start position of a new line
                i = 1        # current position
                count = len(msg)  # length of the whole docstring
                while i < count:
                    wrapped = False  # indicating whether there is a wrapped line
                    newline = ""     # used to insert a '\n'
                    hyphen = ""      # used to insert a '-'

                    if msg[i-1] == "\n":
                        # Indent the new line
                        wrapped = True
                    elif i != i_start and (i - i_start) % wline == 0:
                        # Start a new line and set indentation for it
                        wrapped = True
                        newline = "\n"
                        if not msg[i-1].isspace() and not msg[i].isspace():
                            hyphen = "-"

                    if wrapped:
                        msg = "{}{}{}{}{}".format(msg[:i], hyphen, newline, docind, msg[i:])
                        count = len(msg)
                        i += len(newline) + len(hyphen)
                        i_start = i

                    # pointer increment
                    i += 1

            doc_opts.append(msg)

        print("\nOptions:\n{}\n".format("\n".join(doc_opts)))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
