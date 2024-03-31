#!/usr/bin/env python3

"""Log fields manipulation.

A field object has its name, dtype, fmt, pattern, etc. The attribute dtype
specifies the data type of the field and fmt specifies how to format the
field value.

The LogFields reads default fields from a file at the initialization, so we
need to make sure the data file exists ("default_fields.json").

Classes: Field, LogFields, FieldSpec, FieldPredicate, FieldEncoder, FieldsEncoder

Functions: help_fields, expand_specs, dump, load

Authors: An Wang, USTB (wangan.cs@gmail.com)

Date: 2020/11/16

"""

import collections
import json
import re
import antmocdata.log.fields


class Field(object):
    """A log field.

    Parameters
    ----------
    name : string
        Field name.

    dtype : type, optional (default: str)
        Field value type.

    fmt : string, optional (default: "{}")
        Field value format used for formatted output.

    patterns : string list, optional (default: [])
        Possible perl regex used to read values from log files (TXT serializer only).

    doc : string, optional (default "")
        Field docstring.

    Examples
    --------

    Create a Field object
    >>> field = Field(name="SolutionTime", dtype=float, fmt="{:.5E}")

    Suppose that we have read some value from text
    >>> some_value = "1.123456789E+03"

    Convert the string to the field dtype
    >>> value = field.dtype(some_value)

    Format the value for printing
    >>> field.fmt.format(value)
    '1.12346E+03'

    """

    def __init__(self, name, dtype=str, fmt="{}", patterns=[], doc=""):

        self.name = name
        self.dtype = dtype
        self.fmt = fmt
        self.patterns = patterns
        self.doc = doc

        if not isinstance(dtype, type):
            raise TypeError(f"dtype '{dtype}' is not a type object")

        if not isinstance(fmt, str):
            raise TypeError(f"fmt '{fmt}' is not a string")

        if isinstance(patterns, str):
            self.patterns = [patterns]

    def serialized(self):
        data = {
            "name": self.name,
            "dtype": self.dtype.__name__,
            "fmt": self.fmt,
            "patterns": self.patterns,
            "doc": self.doc,
        }
        return data

    def __str__(self):
        return json.dumps(self, cls=FieldEncoder, indent=2)


class LogFields(object):
    """Log fields.

    This class stores all available fields and their attributes.

    Any new fields should be added below to affect the initialization of a LogFile
    object. Before you trying to define a field, please call help_fields() to check
    the existing fields.

    Examples
    --------

    >>> logfields = LogFields()

    >>> isinstance(logfields, LogFields)
    True

    Add a field
    >>> logfields["NewField"] = Field(name="NewField", patterns=["NewField.*"])

    >>> print(logfields["NewField"].name)
    NewField

    """

    # Singleton
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(LogFields, cls).__new__(cls)

            # Read default fields
            import inspect, os

            path = os.path.dirname(inspect.getfile(antmocdata.log.fields))
            path = os.path.join(path, "default_fields.json")

            # This method will call __new__ again but it will see the instance
            # and return it immediately. It works fine with Python 3.
            load(path)

        return cls.instance

    def __getitem__(self, field_name):
        """Return a Field object by name."""
        return self.data[field_name]

    def __setitem__(self, name, field):
        """Set a Field object by name."""
        if isinstance(field, Field):
            if name != field.name:
                raise KeyError(
                    f"Field name '{field.name}' doesn't match the key '{name}'"
                )
            self.data[name] = field
        else:
            raise TypeError(
                f"Object '{field}' is not a Field and cannot be added to LogFields"
            )

    def __str__(self):
        return json.dumps(self, indent=2, cls=FieldsEncoder)

    def add(self, field):
        """Add a Field object"""
        if isinstance(field, Field):
            self.data[field.name] = field
        else:
            raise TypeError(
                f"Object '{field}' is not a Field and cannot be added to LogFields"
            )

    def items(self):
        """Return tuple list of fields."""
        return self.data.items()

    def keys(self):
        """Return field names."""
        return self.data.keys()

    def values(self):
        """Return field objects."""
        return self.data.values()

    def names(self):
        """Return field names."""
        return self.keys()

    def dtypes(self):
        """Return field dtypes."""
        return [x.dtype for x in self.values()]

    def patterns(self):
        """Return list of field patterns."""
        return [x.patterns for x in self.values()]

    def docs(self):
        """Return field docstrings."""
        return [x.doc for x in self.values()]


class FieldEncoder(json.JSONEncoder):
    """A json encoder for Field."""

    def default(self, field):
        return field.serialized()


class FieldsEncoder(json.JSONEncoder):
    """A json encoder for LogFields."""

    def default(self, fields):
        return [x.serialized() for x in fields.values()]


def decode_field(json_obj):
    """A hook for json.load to decode Field or Field list."""
    types = {"str": str, "int": int, "float": float}

    if "name" in json_obj:
        return Field(
            name=json_obj["name"],
            dtype=types[json_obj["dtype"]],
            fmt=json_obj["fmt"],
            patterns=json_obj["patterns"],
            doc=json_obj["doc"],
        )
    return json_obj


def dump(obj, path, mode="x"):
    """Save a field or fields to a json file."""
    with open(path, mode=mode) as file:
        if isinstance(obj, Field):
            encoder = FieldEncoder
        elif isinstance(obj, LogFields):
            encoder = FieldsEncoder
        else:
            raise NotImplementedError("Only Field or LogFields can be dumped")
        json.dump(obj, fp=file, indent=2, cls=encoder)


def load(path):
    """Load a field or fields from a json file.
    LogFields is currently implemented by singleton, so we have to change its
    attributes after decoding the json file.
    """
    with open(path, mode="r") as file:
        data = json.load(fp=file, object_hook=decode_field)
        if isinstance(data, Field):
            return data

        # The data is supposed to be a list of fields
        try:
            logfields = LogFields()
            logfields.data = collections.OrderedDict()
            for field in data:
                logfields.data[field.name] = field
            return logfields
        except:
            raise NotImplementedError("Only Field or LogFields can be loaded")


def add(field):
    """Add a field to LogFields object

    >>> add(Field(name="NewField", patterns=["NewField.*"]))
    """
    LogFields().add(field)


def help_fields():
    """Help message for available fields."""

    logfields = LogFields()
    wfield = max([len(x) for x in logfields.names()])
    wtype = max([len(x.__name__) for x in logfields.dtypes()])
    msg = []
    for field in logfields.values():
        type_str = f"({field.dtype.__name__})"
        msg.append(f"{field.name: <{wfield}}{type_str: <{wtype+2}} : {field.doc}")

    print("\nAvailable fields:\n{}\n".format("\n".join(msg)))


class FieldSpec(object):
    """Field name pattern and predicate.

    Field spec consists of a field name and a predicate.
    The field name is a perl regex without symbols "=", "<", and ">".
    The predicate is an op and value. The operator can be "==", "<",
    "<=", ">", and ">=", or just an empty string. The value is a perl
    regex. Wildcards in the value only work when the operator is set
    to "==".

    For example, the following spec has a field name of "JobId", an op
    of "==", and a value of "2020.*".
        "JobId=2020.*"

    When it is used to instantiate a FieldSpec, it will be unpacked to
        ("JobId", "==", "2020.*")

    A minimal field spec contains only a field name.

    Parameters
    ----------
    spec : string
        A string representation of a field spec.

    Attributes
    ----------
    name  : string
        Field name, perl regex is supported
    op    : string
        Binary oprator in ["", "==", "<", "<=", ">", ">="], "" represents always-true
    value : string
        Value/regex for comparison (combined with op as a predicate for filtering)

    Examples
    --------

    >>> spec = FieldSpec("JobId==2020")

    >>> spec.name
    'JobId'

    >>> FieldSpec("JobId").get()
    ('JobId', '', '')

    >>> FieldSpec("JobId==2020.*").get()
    ('JobId', '==', '2020.*')

    >>> FieldSpec("JobId<2020").get()
    ('JobId', '<', '2020')

    >>> FieldSpec("JobId>2020").get()
    ('JobId', '>', '2020')

    >>> FieldSpec("JobId<=2020").get()
    ('JobId', '<=', '2020')

    >>> FieldSpec("JobId>=2020").get()
    ('JobId', '>=', '2020')

    >>> FieldSpec("JobId=2020").get()
    Traceback (most recent call last):
        ...
    ValueError: Failed to unpack field spec 'JobId=2020'

    >>> FieldSpec("==2020").get()
    Traceback (most recent call last):
        ...
    ValueError: Failed to unpack field spec '==2020'

    Be careful, this will be treated as a single regex
    >>> FieldSpec("JobId+2020").get()
    ('JobId+2020', '', '')

    >>> FieldSpec("JobId==").get()
    Traceback (most recent call last):
        ...
    ValueError: An op or value is missing in field spec 'JobId=='

    Expand the spec by field name
    >>> spec = FieldSpec("J[a-z]*Id==2020.*")

    >>> spec.get()
    ('J[a-z]*Id', '==', '2020.*')

    >>> specs = spec.expanded()

    >>> [str(x) for x in specs]
    ['JobId==2020.*']

    """

    def __init__(self, spec):
        """Unpack a field spec string."""

        re_matched = re.match(r"^([^<=>]+)([<>]=?|==)?([^<=>]*)$", spec)
        if re_matched:
            name, op, value = re_matched.groups()
            op = "" if op is None else op
            value = "" if value is None else value
        else:
            raise ValueError(f"Failed to unpack field spec '{spec}'")

        # Check if value comes along with op
        if op and not value or not op and value:
            raise ValueError(f"An op or value is missing in field spec '{spec}'")

        # Set attributes
        self.name = name
        self.op = op
        self.value = value

        # This attribute can only be set to a concrete Field spec
        self.pred = None

    def __str__(self):
        return f"{self.name}{self.op}{self.value}"

    def get(self):
        """Return this spec in a tuple."""
        return self.name, self.op, self.value

    def expanded(self):
        """Return the expanded list of this spec.

        The field name will be expanded to concrete names by the regex it
        indicated. Each of the concrete field name will be paired with a
        FieldPredicate object to create a new spec object.

        Returns
        -------
        [specs] : list of FieldSpec objects

        """

        # A list of field specs
        specs = []

        # Set the regex to field name
        re_field = re.compile(f"^{self.name}$")

        # Search for matched names
        for field_name in LogFields().names():
            re_matched = re_field.match(field_name)
            if re_matched:
                # Create a predicate for the spec
                spec = FieldSpec(f"{re_matched.group()}{self.op}{self.value}")
                spec.pred = FieldPredicate(
                    name=re_matched.group(), op=self.op, value=self.value
                )
                specs.append(spec)

        if not specs:
            raise KeyError(f"No field name matches pattern '{self.name}'")

        return specs


class FieldPredicate(object):
    """Predicate for log file filtering.

    If op is "==", values are treated as strings and the comparison is to be
    done by regex matching (just like "=~"). In other cases, values will be
    typed and the type should be the same as the field dtype.

    Parameters
    ----------
    spec : string
        A string represents a field pred.

    Examples
    --------

    Binary operator "==" for strings
    >>> pred = FieldPredicate("JobId", "==", "31623.*")

    >>> pred("1")
    False

    >>> pred("31623")
    True

    >>> pred("316231421")
    True

    Binary operator "<" for strings or integers
    # >>> pred = FieldPredicate("JobId", "<", "31623")

    # >>> pred("1")
    # True

    # >>> pred("99999")
    # False

    Binary operator ">=" for integers
    >>> pred = FieldPredicate("Azims", ">=", "32")

    >>> pred("8")
    False

    >>> pred("32")
    True

    >>> pred("64")
    True

    Always-true operator
    >>> pred = FieldPredicate("JobId")

    >>> pred("123")
    True

    >>> pred([1, 2, 3])
    True

    """

    def __init__(self, name, op="", value=""):

        # Set attributes
        self.name = name
        self.dtype = LogFields()[name].dtype
        self.op = op
        self.value = value

        if self.op == "==":
            self.re_value = re.compile(str(self.value), re.I)

        if self.op in ["<", "<=", ">", ">="]:
            try:
                self.value = self.dtype(self.value)
            except:
                raise TypeError(
                    f"Value '{self.value}' is not of the dtype '{self.dtype}' of field '{name}'"
                )

    def __call__(self, value):

        if not self.op:
            # If op is not set, match all values
            return True

        if not value:
            # If the given value is None, return false.
            # FIXME: This behaviour will skip fields without values, which
            # prevents a spec to match empty fields directly.
            return False

        if self.op == "==":
            # Treat "==" as "=~"
            return self.re_value.match(str(value)) is not None

        # Check the value type and convert it to field dtype
        try:
            value = self.dtype(value)
        except:
            raise TypeError(
                f"Value '{value}' is not of the dtype '{self.dtype}' of field '{self.name}'"
            )

        match self.op:
            case "<":
                return value < self.value
            case "<=":
                return value <= self.value
            case ">":
                return value > self.value
            case ">=":
                return value >= self.value
            case _:
                raise ValueError(
                    f"Unsupported operator '{self.op}' in field predicate '{self.name}{self.op}{self.value}'"
                )

    def __str__(self):
        return f"{self.op}{self.value}"


def expand_specs(field_specs):
    """Expand specs to be lists of (name, pred) tuples.

    Each spec will be expanded to a list of (name, pred) tuples.

    Examples
    --------

    >>> specs = ["J[a-z]*Id", "Job.*", "Job.*==2020.*"]

    >>> specs = expand_specs(specs)

    >>> [str(x) for x in specs]
    ['JobId', 'JobId', 'JobId==2020.*']

    """

    specs = []
    for spec_str in field_specs:

        # Expand field spec name and predicates
        specs.extend(FieldSpec(spec_str).expanded())

    return specs


if __name__ == "__main__":
    import doctest

    doctest.testmod()
