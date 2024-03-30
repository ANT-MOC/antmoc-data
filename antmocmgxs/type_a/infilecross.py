"""Utils for parsing 'infilecross' files.

Functions:
    read_element_map(...)
    parse_nuclide_name(...)
    parse_count_nuclides_groups(...)
    parse_xs_arrays(...)
    parse_scatter_matrix(...)
    parse_nuclideset(...)
    find_nuclidesets(...)

Author: An Wang, USTB (wangan.cs@gmail.com)
Date:   November 17, 2020
"""

import json
import pathlib
import re
import warnings
import numpy as np
from . import nuclides


def read_element_map(jsonfile):
    """Read element definitions from a json file.

    This function generate a dictionary which maps element names to numbers.
    Each of the value is an array of integers, which contains the element
    number and an optional mass number.

    Parameters
    ----------
    jsonfile : name of a json file.

    """
    with open(jsonfile) as file:
        elements = json.load(file)

    # Convert keys to uppercase
    elements_upper = {}
    for key, value in elements.items():
        elements_upper[key.upper()] = value

    return elements_upper


def parse_nuclide_name(string, elementmap=None):
    """Parse a name to get the atomic number and mass of an element.

    The name is read from a file formed like 'infilecross', which is filled
    with data of nuclide sets.
    The name consists of a string and an extra mass number. If the mass
    number is missing, it must be specified in the elementmap.

    Parameters
    ----------
    string : element name in string.
    elementmap : file containing an elements map (defaults to "elements.json")

    Return
    ------
    name, number, mass

    Examples
    --------
    Name and mass separated by a hyphen
    >>> Cr_50 = parse_nuclide_name("CHROMIUM-50")

    >>> print(Cr_50)
    ('CHROMIUM', 24, 50)

    Compact form of abbreviated name
    >>> U_235 = parse_nuclide_name("U235.PF")

    >>> print(U_235)
    ('U', 92, 235)

    A single line in 'infilecross' file
    >>> Cr_50 = parse_nuclide_name("0002405002  0  3  CHROMIUM-50")

    >>> print(Cr_50)
    ('CHROMIUM', 24, 50)

    """
    # Initialize the elements map as needed.
    #   element name -> [number] or [number, mass]
    if not elementmap:
        path = pathlib.Path(__file__).parent.absolute() / "elements.json"
        elementmap = str(path)
    elementmap = read_element_map(elementmap)

    # Patterns for extracting the name and mass
    name_patterns = [
        r"[^a-z\.]*([a-z]+)-([0-9]+)[ \t]*",
        r"[^a-z\.]*([a-z]+)([0-9]+)[^0-9]*[ \t]*"
    ]

    # Parse the name for the atomic number and mass.
    for pattern in name_patterns:
        re_matched = re.match(pattern, string, re.I)
        if re_matched:
            name = re_matched.group(1).upper()
            mass = re_matched.group(2)

            if name in elementmap:
                number = elementmap[name][0]
            else:
                raise KeyError(
                    f"When parsing '{string}': failed to find '{name}' in file '{elementmap}'"
                    )
            break

    if not re_matched:
        raise ValueError(f"When parsing '{string}': unknown name pattern")

    return name, int(number), int(mass)


def parse_nuclideset_id(string):
    """Parse a string for NuclideSet ID.

    Given a string like
        "$SOMESTRING 1 7SETs SET1"
    or
        "$SOMESTRING 1 7SETs 1SET"
    The ID 1 will be extracted from 'SET1' or '1SET'.

    Examples
    --------
    >>> parse_nuclideset_id("$Some string 1 7SETs 2SET")
    2

    >>> parse_nuclideset_id("$Some string 1 7SETs SET2")
    2
    """
    patterns = [
        r'[ \t]*\$.*SET([0-9]+)[ \t]*$',
        r'[ \t]*\$.*([0-9]+)SET[ \t]*$',
    ]

    for pattern in patterns:
        re_matched = re.search(pattern, string, re.I)
        if re_matched:
            break

    if not re_matched:
        raise ValueError(
            f"Failed to find the number of sets in the following string:\n"
            f"\n{string.encode('unicode_escape')}\n\n"
            f"Patterns searched:\n"
            "{}".format('\n'.join(patterns))
            )

    return int(re_matched.group(1))


def parse_count_nuclides_groups(string):
    """Parse a string for the number of nuclides and the number of energy groups.

    Given a string like
        "    2  30  6  5  0  0"
    The number of nuclides is 30 and the number of energy groups is 6.

    Return
    ------
    nnuclides, ngroups

    Examples
    --------
    >>> parse_count_nuclides_groups("2 30 6 5 0 0")
    (30, 6)
    """
    array = [int(word) for word in string.strip().split()]

    if len(array) < 6:
        raise ValueError(
            f"Failed to find the number of nuclides and groups in string:\n"
            f"\n{string.encode('unicode_escape')}\n\n"
            "The string must contain at least 6 whole numbers."
            )

    if array[1] < 1 or array[2] < 1:
        reportname = "nuclides" if array[1] < 1 else "energy groups"
        raise ValueError(
            f"In string:\n"
            f"\n{string.encode('unicode_escape')}\n\n"
            f"The number of {reportname} {array[1]} is less than 1."
            )

    return array[1], array[2]


def parse_chi(string):
    """Parse a string for Chi."""
    chi = [np.float64(word) for word in string.strip().split()]

    if len(chi) == 0:
        raise ValueError("Failed to parse an empty string for Chi")

    return chi


def parse_xs_arrays(strings, xsindices=None):
    """Parse an array of strings for cross-sections except the scatter matrix.

    Given an array like
        [
            "0.1505E-02  0.6758E-05  0.1733E+01  0.2000E+01  0.6758E-05  0.0+00",
            "0.2867E-03  0.0000E+00  0.2946E+01  0.0000E+00  0.0000E+00  0.0+00"
        ]
    and an xsindices
        {
            "absorption": 0,
            "fission": 1,
            "transport": 2,
            "nu": 3
        }

    The function returns a dictionary as follow
        {
            "absorption": [0.1505E-02, 0.2867E-03],
            "fission": [0.6758E-05, 0],
            "transport": [0.1733E+01, 0.2946E+01],
            "nu": [0.2E+01, 0]
        }

    Parameters
    ----------
    strings : a string arrays consisting of cross-sections in the column-major order.
    xsindices : column indices of each cross-section array (defaults to None).

    Return
    ------
    A dictionary of cross-section arrays.
    """
    # Use the default xsindices if it is missing.
    if not xsindices:
        xsindices = {
            "absorption": 0,
            "fission": 1,
            "transport": 2,
            "nu": 3
        }

    # Find the maximum column index
    n_columns_required = max(xsindices.values()) + 1

    # Initialize the result dictionary
    xs_data = {}
    for xs_name in xsindices:
        xs_data[xs_name] = []

    for string in strings:
        array = [np.float64(word) for word in string.strip().split()]

        # Check if there are enough lines to read
        if len(array) < n_columns_required:
            raise ValueError(
                f"Failed to read xs data from string:\n"
                f"\n{string.encode('unicode_escape')}\n\n"
                f"The index map requires at least {n_columns_required} columns "
                f"but only {len(array)} was found in the string.\n"
                f"Index map = {xsindices}"
                )

        for xs_name in xsindices:
            idx = xsindices[xs_name]
            xs_data[xs_name].append(array[idx])

    return xs_data


def parse_scatter_matrix(strings):
    """Parse an array of strings for a scatter matrix.

    Given an matrix like
        [
            "0.2054E+01  0.5554E+00",
            "0.0000E+00  0.3412E+01"
        ]

    The function returns an array as follow
        [0.2054E+01, 0.5554E+00, 0.0000E+00, 0.3412E+01]

    Parameters
    ----------
    strings : a string arrays consisting of a matrix.

    Return
    ------
    An array of the flattened scatter matrix.
    """
    scatter_matrix = []
    ngroups = len(strings[0].strip().split())

    for string in strings:
        array = [np.float64(word) for word in string.strip().split()]

        if len(array) != ngroups:
            raise ValueError(
                f"Failed to read sigma_s from string:\n"
                f"\n{string.encode('unicode_escape')}\n\n"
                f"The number of energy groups required is {ngroups} but {len(array)} was found"
                )

        scatter_matrix.extend(array)

    return scatter_matrix


def _parse_nuclide(strings, ngroups, marks=None, xsindices=None):
    """Parse an array of strings for a Nuclide object.

    The array of strings must follow the format of 'infilecross' files. It must contains
        - section 'header': a line containing the nuclide identification.
        - section 'xs': lines of cross-section arrays.
    Each of the sections are marked with a name and an index. The marks are given by
    the argument 'marks'.

    Parameters
    ----------
    strings : a string arrays indicating a NuclideSet.
    ngroups : number of energy groups.
    marks : line numbers of data sections (1-based).

    Examples
    --------
    The following nuclide has data of 3 energy groups. The marks is supposed to be
        {
            "header": 1,
            "xs": 12
        }

    Plain text:
        2511102302   0   3   6SODIUM-23
        # 10 extra lines goes here, and then the data section.
        # So the first data section starts at line 12.
        0.15056647E-02  0.67588903E-05  0.17331473E+01  0.20000000E+01  0.67588903E-05
        0.28678903E-03  0.00000000E+00  0.29464412E+01  0.00000000E+00  0.00000000E+00
        0.93697878E-02  0.00000000E+00  0.30961969E+01  0.00000000E+00  0.00000000E+00
        0.20543602E+01  0.55545408E+00  0.17748818E-01
        0.00000000E+00  0.34123311E+01  0.61543798E+00
        0.00000000E+00  0.00000000E+00  0.36163757E+01
    """
    # Set up the default marks
    if not marks:
        marks = {
            "header": 1,
            "xs": 12
        }

    if min(marks.values()) < 1:
        raise ValueError(
            f"Failed to read a nuclide.\n"
            f"Line number less than 1 found in marks:\n{marks}"
            )

    header_idx = marks["header"] - 1
    name, number, mass = parse_nuclide_name(strings[header_idx])
    nuclide = nuclides.Nuclide(name=name, number=number, mass=mass, ngroups=ngroups)

    # Parse the strings for cross-section arrays
    xs_idx = marks["xs"] - 1
    xs_data = parse_xs_arrays(
        strings=strings[xs_idx:xs_idx+ngroups],
        xsindices=xsindices
    )

    for xs_name, xs_array in xs_data.items():
        nuclide[xs_name] = xs_array

    # Parse the strings for the scatter matrix
    matrix_idx = xs_idx + ngroups
    nuclide["scatter matrix"] = parse_scatter_matrix(
        strings=strings[matrix_idx:matrix_idx+ngroups]
    )

    return nuclide


def parse_nuclideset(strings, setmarks=None, nuclidemarks=None, xsindices=None):
    """Parse an array of strings for a NuclideSet object.

    The array of strings must follow the format of 'infilecross' files. It must contains
        - section 'header': a mark '$' indicating the beginning of the set.
        - section 'counts': a line containing the number of nuclides and energy groups.
        - section 'chi': a line of array Chi.
        - section 'nuclides': several nuclide data sections.
    Each of the sections are labeled with a name and an index. The marks are given by
    the argument marks.

    Parameters
    ----------
    strings : a string arrays indicating a NuclideSet.
    setmarks : line numbers of nuclide set data sections (1-based).
    nuclidemarks : line numbers of nuclide data sections (1-based).
    xsindices : column indices of each cross-section array (see parse_xs_arrays).

    Examples
    --------

    The following set contains 30 nuclide sections. The setmarks is supposed to be
        {
            "header": 1,
            "counts": 2,
            "chi": 3,
            "nuclides": 9
        }

    Plain text:
        $SOMESTRING 1  7SETs 1SET
           2  30   3   5   0   0
          0.57564402E+00  0.29341474E+00  0.12731624E+00
          # 5 extra lines goes here, and then data sections of nuclides.
          # So the first nuclide data section starts at line 9.
          2511102302   0   3   6SODIUM-23
          ...
          4311402802   0   3   6SILICON-28
          ...
    """

    # Set up the default setmarks
    if not setmarks:
        setmarks = {
            "header": 1,
            "counts": 2,
            "chi": 3,
            "nuclides": 9
        }

    if min(setmarks.values()) < 1:
        raise ValueError(
            f"Failed to read a nuclide set.\n"
            f"Line number less than 1 found in marks:\n{setmarks}"
            )

    # Parse the strings for nuclide set information
    nuclideset = nuclides.NuclideSet()
    nuclideset.uid = parse_nuclideset_id(
        strings[setmarks["header"] - 1]
        )
    nuclideset.nnuclides, nuclideset.ngroups = parse_count_nuclides_groups(
        strings[setmarks["counts"] - 1]
        )
    nuclideset.chi = np.array(
        parse_chi(strings[setmarks["chi"] - 1])
        )

    # Determine the number of lines for a nuclide
    start_idx = setmarks["nuclides"] - 1
    end_idx = start_idx + 1
    while end_idx < len(strings):
        string = strings[end_idx]
        try:
            parse_nuclide_name(string)
        except ValueError:
            if re.search(r"[a-z]+[a-z]+", string, re.I):
                warnings.warn(
                    f"While reading nuclide set {nuclideset.uid}, "
                    f"a line containing words was skipped:\n"
                    f"\n{string.encode('unicode_escape')}\n\n"
                    f"This could be a mistake."
                    )
        except Exception as e:
            raise e
        else:
            break
        end_idx += 1

    if end_idx == len(strings):
        end_idx -= 1

    rows_nuclide = end_idx - start_idx

    # Check whether there are enough strings to parse
    min_rows_nuclide = 1 + 2 * nuclideset.ngroups
    if rows_nuclide < min_rows_nuclide:
        raise ValueError(
            f"Failed to read nuclide set {nuclideset.uid} from strings:\n"
            "\n{}\n\t... {} more lines\n\n".format("\n".join(strings[:15]), len(strings)-15) +
            f"{min_rows_nuclide} lines required for the first nuclide "
            f"but {rows_nuclide} was found.\n"
            )

    rows_required = max(setmarks.values()) - 1 + rows_nuclide * nuclideset.nnuclides
    if len(strings) < rows_required:
        actual_n_nulicdes = (len(strings) - max(setmarks.values()) + 1) // rows_nuclide
        warnings.warn(
            f"Failed to read nuclide set {nuclideset.uid} from strings:\n"
            "\n{}\n\t... {} more lines\n\n".format("\n".join(strings[:15]), len(strings)-15) +
            f"{rows_required} lines required for the nuclide set but {len(strings)} was found.\n"
            f"Number of nuclides expected: {nuclideset.nnuclides}\n"
            f"Number of nuclides found: {actual_n_nulicdes}\n"
            f"Rows of a nuclide data section: {rows_nuclide}\n"
            f"There might be a mistake either in the input or in the code. "
            f"Missing nuclides will be skipped and the number of nuclides will be "
            f"set to {actual_n_nulicdes}.\n"
            )

        nuclideset.nnuclides = actual_n_nulicdes

    # Parse the rest of the strings for nuclides
    for i in range(nuclideset.nnuclides):
        start_idx = setmarks["nuclides"] - 1 + i * rows_nuclide
        end_idx = start_idx + rows_nuclide
        nuclideset.add_nuclide(
            _parse_nuclide(
                strings=strings[start_idx:end_idx],
                ngroups=nuclideset.ngroups,
                marks=nuclidemarks,
                xsindices=xsindices
            )
        )

    return nuclideset


def find_nuclidesets(strings, setmarks=None, nuclidemarks=None, xsindices=None):
    """Find all NuclideSet data sections in an array of strings.

    This function simply calls parse_nuclideset(...) multiple times to get all of the
    NuclideSet data sections from a string array.

    The string array usually consists of all lines of an "infilecross" file.

    Parameters
    ----------
    See function parse_nuclideset(...)

    Return
    ------
    A dictionary of NuclideSet object indexed by set ID.
    """

    # Each of the nuclide set sections starts with a line marked by "$"
    def find_start(strings, pos=0):
        start_mark = r"[ \t]*\$.*"
        while pos < len(strings):
            if re.match(start_mark, strings[pos]):
                return pos
            pos += 1
        return len(strings)

    nuclidesets = {}
    end = -1

    while end < len(strings):
        start = find_start(strings, end)
        end = find_start(strings, start + 1)

        if start < end:
            nuclideset = parse_nuclideset(
                strings=strings[start:end],
                setmarks=setmarks,
                nuclidemarks=nuclidemarks,
                xsindices=xsindices
            )
            nuclidesets[nuclideset.uid] = nuclideset
        else:
            break

    return nuclidesets


if __name__ == "__main__":
    import doctest
    doctest.testmod()
