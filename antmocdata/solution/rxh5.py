#!/usr/bin/env python3
"""
Tools for HDF5 files of reaction rates and fluxes.

Author: An Wang, USTB (wangan.cs@gmail.com)
"""

import numpy as np
import h5py
from pyevtk.hl import pointsToVTK


def _get_numpy_array(hdf5_group, key):
    """A helper routine to ensure that the data is a proper NumPy array"""

    data_array = np.array(hdf5_group[f"{key}/"][...])
    data_array = np.atleast_1d(data_array)
    data_array = data_array.flatten()
    return data_array


def convert_h5_to_vtk(file, out=None):
    """Load an HDF5 solution file and convert it to a VTK file

    Parameters
    ----------
    file : file path or file object of the HDF5 solution file
    out : output file name
    """

    # Create a h5py file handle for the file
    if isinstance(file, str):
        file = h5py.File(file, "r")

    # Specify the data source
    domain_type = "FSR"

    # Check that the file has an 'fsrs' attribute
    if "# fsrs" not in file.attrs:
        raise ValueError(f'Failed to load {file.filename}: missing attribute "# fsrs"')

    if domain_type not in file.keys():
        raise ValueError(
            f'Failed to load {file.filename}: missing domain type "{domain_type}"'
        )

    # Check that the file has FSR points or centroids
    point_types = ["Points", "Centroids"]
    point_type = ""
    for t in point_types:
        if t in file[domain_type]:
            point_type = t
            break
    if point_type in point_types:
        print(f'FSR point type is "{point_type}"')
    else:
        raise ValueError(
            f"Failed to parse {file.filename}: missing valid FSR point type (Points or Centroids)"
        )

    # Each of the tally type has several datasets
    tally_types = [
        "Fission RX",
        "NuFission RX",
        "Total RX",
        "Absorption RX",
        "Scalar Flux",
        "Fission XS",
        "NuFission XS",
        "Total XS",
        "Absorption XS",
    ]

    # Instantiate dictionary to hold FSR data
    fsr_points = {}
    fsr_data = {}
    num_fsrs = int(file.attrs["# fsrs"])

    # Iterate over all domains (e.g., fsrs, tracks) in the HDF5 file
    domain_obj = file[domain_type]
    for group_name in sorted(domain_obj):

        print(f'Found data for {domain_type} "{str(group_name)}"')

        # Create shortcut to HDF5 group for this domain
        group_obj = domain_obj[group_name]

        # Read FSR centroids from the file
        if group_name in point_types:
            if group_name == point_type:
                print(f"Importing data for {group_name} X Y Z")
                fsr_points["X"] = _get_numpy_array(group_obj, "X")
                fsr_points["Y"] = _get_numpy_array(group_obj, "Y")
                fsr_points["Z"] = _get_numpy_array(group_obj, "Z")

        # Read FSR volumes from the file
        elif group_name == "Volumes":
            print(f"Importing data for {group_name}")
            fsr_data[group_name] = _get_numpy_array(domain_obj, group_name)

        # Read reaction rates from the file
        elif group_name in tally_types:
            for energy_name in sorted(group_obj):

                # Set the name of the data array
                array_name = group_name
                if "sum" != energy_name:
                    array_name = array_name + " " + energy_name

                print(f"Importing data for {array_name}")

                fsr_data[array_name] = _get_numpy_array(group_obj, energy_name)

        else:
            print(f'Unknown dataset name: "{group_name}"')

    # Write the data to a VTK file
    if out is None:
        path = file.filename.rpartition(".")[0]
    else:
        path = out
    path = pointsToVTK(path, fsr_points["X"], fsr_points["Y"], fsr_points["Z"], fsr_data)

    print(f'Finished writing VTK data to "{path}"')
    print(f"The number of FSRs is {num_fsrs}")
