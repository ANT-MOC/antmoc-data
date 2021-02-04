"""Class Material

Author: An Wang, USTB (wangan.cs@gmail.com)
Date:   October 4, 2020
"""

import copy
import warnings
import numpy as np


class Material:
    """The representation for Material used as antmoc input.

    Not all of the cross-section arrays are required for an antmoc run. For example,
    array 'transport' is alternate to array 'total', so thery would never be used by
    antmoc in the same time.

    The scatter matrix could contains high-order data. If that is so, the scatter
    data would be stored as a two-dimentional array with data of the ith order in
    the ith row.

        [... 0th order scatter matrix ...]
        [... 1th order scatter matrix ...]
        ...

    Attributes
    ----------
    name : string
        a unique identification, this is also the H5 group name
    info : string
        an optional description
    data : dictionary {xsname: data_array}
        cross-section arrays, each of which is a numpy.array object
    ngroups: int
        number of energy groups

    Examples
    --------
    Instantiate a material
    >>> material = Material(name="EEZO", info="Element Zero", ngroups=0)

    >>> print(material.name)
    EEZO

    """
    # Data entry names required by antmoc.
    xslist = [
        "absorption",
        "fission",
        "total",
        "transport",
        "nu-fission",
        "chi",
        "scatter matrix",
    ]

    # An index map for compressed layout.
    # These indices are to be written to the H5 file as top-level attributes.
    # Attribute names must has a leading 'idx'. For example,
    #   /material/idx absorption : 0
    #   /material/idx fission : 1
    #   /material/idx transport : 2
    xsindices = {
        "absorption": 0,
        "fission": 1,
        "transport": 2,
        "nu-fission": 3,
        "chi": 4,
    }

    def __init__(self, name="unnamed", info="", ngroups=0, data=None):
        # Unique name
        self.name = str(name)

        # A short description
        self.info = str(info)

        # Number of energy groups
        self.ngroups = int(ngroups)

        # Cross-sections
        if data:
            self.data = data
        else:
            self.data = {}

    def __getitem__(self, xsname):
        return self.data[xsname]

    def __setitem__(self, xsname, value):
        if xsname not in Material.xslist:
            raise KeyError(f"Undefined cross-section name: {xsname}")
        self.data[xsname] = value

    def __eq__(self, other):
        """Comparison operator.
        Two materials are considered equal if they have the same name, number of
        energy groups, and cross-sections.
        """
        if isinstance(other, Material):
            is_equal = self.name == other.name \
                and self.ngroups == other.ngroups \
                and len(self.data) == len(other.data)

            if not is_equal:
                return False

            for xsname in self.data:
                if not np.array_equal(self.data[xsname], other.data[xsname]):
                    return False

            return True
        return NotImplemented

    def __str__(self):
        string = f"Material:\n" \
            f"\tname = '{self.name}'\n" \
            f"\tinfo = '{self.info}'\n" \
            f"\tnumber of groups = {self.ngroups}\n"

        string += "\tcross-sections:\n"
        for name, array in self.items():
            string += f'\t{name: <14} = {array}\n'

        return string

    def items(self):
        """Return items of the xs dictionary."""
        return self.data.items()

    def keys(self):
        """Return keys of the xs dictionary."""
        return self.data.keys()

    def values(self):
        """Return values of the xs dictionary."""
        return self.data.values()

    def copy(self):
        """Deep copy."""
        return Material(
            name=self.name,
            info=self.info,
            ngroups=self.ngroups,
            data=copy.deepcopy(self.data)
            )

    def scatter_matrix(self, order=0):
        """Return the scatter matrix of a specified order."""
        if self['scatter matrix'].ndim > 1:
            return self['scatter matrix'][order, :]
        return self['scatter matrix']

    def _check_xs_size(self):
        """Check sizes of each array."""
        for xsname, array in self.items():
            if xsname.find("scatter") >= 0:
                array = array.flatten()
                squaregroups = self.ngroups * self.ngroups
                if len(array) % (squaregroups) != 0:
                    raise ValueError(
                        f"Array '{xsname}' has length {len(array)} which is not "
                        f"divisible by ngroups*ngroups ({squaregroups})")
            elif len(array) != self.ngroups:
                raise ValueError(
                    f"Array '{xsname}' has length {len(array)} which not "
                    f"equals ngroups ({self.ngroups})")

    def dump(self, parent, layout="named"):
        """Dump the material to an H5 group

        The material will be written to the file as a subgroup named by the
        material name.

        Parameters
        ----------
        parent : H5 group object
            the parent group of materials, which is often set to '/material'.
        layout : string
            material data layout, either 'named' or 'compressed'/'compact'.
        """
        # Check array sizes
        self._check_xs_size()

        layout_upper = layout.upper()
        if layout_upper in ["NAMED", "OPENMOC"]:
            self._dump_h5_named(parent)
        elif layout_upper in ["COMPRESSED", "COMPACT"]:
            self._dump_h5_compact(parent)
        else:
            raise ValueError(f"Undefined material data file layout: {layout}")

        self._dump_h5_attributes(parent)

    def _dump_h5_named(self, parent):
        """Dump the material with layout 'named'."""
        # Create a subgroup for the material
        h5group = parent.create_group(str(self.name))

        # Dump cross-sections to the file
        for xsname, array in self.items():
            h5group.create_dataset(xsname, data=array.flatten(), dtype=np.float64)

    def _dump_h5_compact(self, parent):
        """Dump the material with layout 'compressed'/'compact'."""
        # Create a subgroup for the material
        h5group = parent.create_group(str(self.name))

        columns = int(max(Material.xsindices.values())) + 1

        # Build the 'reactions' dataset and dump it into the file
        reactions = np.zeros(shape=(self.ngroups, columns), dtype=np.float64)
        for xsname, xsindex in Material.xsindices.items():
            reactions[:, xsindex] = self[xsname]

        h5group.create_dataset('reactions', data=reactions, dtype=np.float64)

        # Reshape the scatter matrix and dump it into the file
        scatter = np.reshape(self['scatter matrix'], (self.ngroups, self.ngroups))
        h5group.create_dataset('scattering', data=scatter, dtype=np.float64)

    def _dump_h5_attributes(self, parent):
        """Define additional H5 attributes for the material.

        Parameters
        ----------
        parent : H5 group object
            the parent group of materials, which is often set to '/material'.
        """
        h5group = parent[str(self.name)]

        # Description
        if self.info:
            h5group.attrs["info"] = self.info

    def load(self, group, layout="named"):
        """Load the material from an H5 group

        Parameters
        ----------
        group : H5 group object
            the associated group of the material
        layout : string
            material data layout, either 'named' or 'compressed'/'compact'.
        """
        # Read material name and extra attributes
        self.name = group.name.split("/")[-1]
        self._load_h5_attributes(group)

        if layout.lower() in ["named", "openmoc"]:
            self._load_h5_named(group)
        elif layout.lower() in ["compressed", "compact"]:
            self._load_h5_compact(group)
        else:
            raise ValueError(f"Undefined material data file layout: {layout}")

        # Check array sizes
        self._check_xs_size()

        if not self.data:
            warnings.warn(f"An empty material {self.name} was read")

    def _load_h5_named(self, group):
        """Load the material with layout 'named'."""
        for xsname in Material.xslist:
            if xsname in group:
                self[xsname] = np.array(group[xsname], dtype=np.float64)

    def _load_h5_compact(self, group):
        """Load the material with layout 'compressed'/'compact'."""
        # Read dataset 'reactions'
        dataset = group['reactions']

        columns = int(max(Material.xsindices.values())) + 1

        # Check dataset dimensions
        if dataset.shape[0] != self.ngroups or dataset.shape[1] < columns:
            raise ValueError(
                f"Failed to read dataset '{dataset.name}' from a 'compact' H5 file:\n"
                f"Bad dataset shape {dataset.shape}")

        for xsname, xsindex in Material.xsindices.items():
            self[xsname] = np.array(dataset[:, xsindex], dtype=np.float64)

        # Read dataset 'scattering'
        dataset = group['scattering']

        if dataset.shape[0] != dataset.shape[1]:
            raise ValueError(
                f"Failed to read dataset '{dataset.name}' from a 'compact' H5 file:\n"
                f"Bad dataset shape {dataset.shape}")

        self["scatter matrix"] = np.array(dataset[...], dtype=np.float64).flatten()

    def _load_h5_attributes(self, group):
        """Read additional H5 attributes for the material."""
        if "info" in group.attrs:
            self.info = group.attrs["info"]

    def build_sigma_total(self):
        """Return the sum of 'absorption' and 'scatter'."""
        # Select the first row of the scatter data (0th order)
        scatter = self.scatter_matrix(0)

        # Add 'scatter' to array 'absorption'
        sigma_total = self["absorption"].copy()
        for group in range(self.ngroups):
            # Starting and end positions of a single energy group
            start = group * self.ngroups
            end = start + self.ngroups
            sigma_total[group] += np.sum(scatter[start:end])
        return sigma_total

    def fix_scatter_matrix(self):
        """Add 'transport' - 'total' to the diagonal elements of the scatter matrix.

        This method only works for the 0th order data.

        'transport' = 'transport'
        Diag(scatter matrix) += 'transport' - 'total'
        """
        # Build the array of sigma total, substract it from 'transport'
        delta = self["transport"] - self.build_sigma_total()

        # Add ('transport' - 'total') to the scatter matrix
        for group in range(self.ngroups):
            # Starting and end positions of a single energy group
            start = group * self.ngroups

            # Add the delta to diagonal elements
            self["scatter matrix"][start+group] += delta[group]

    def fix_sigma_total(self):
        """Take the sum of 'absorption' and 'scatter' as 'total'."""
        self["total"] = self.build_sigma_total()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
