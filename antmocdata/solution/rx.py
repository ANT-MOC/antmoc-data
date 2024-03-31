#!/usr/bin/env python3
"""
Tools for converting files of reaction rates and fluxes to other formats.

Author: An Wang, USTB (wangan.cs@gmail.com)
"""

import re
import xml.etree.ElementTree as ET
import numpy as np

def load_vtu(file, filters = []):
    """Converts a VTK formatted mesh into numpy arrays.
    This method takes the .vtu output of ANT-MOC as its argument and
    extracts data at all the z-sections. All the reaction rates are
    dumped into a numpy array dictionary.
    
    The axes in the .vtu file are
      z     y
      ▲   ▼
      │  /
      │ /
      └───► x

    For convenience, the y-axis is reverted to match the index order of numpy arrays.
        z,i
        ▲
        │
        │
        └────► x,k
       /
      ▼
      y,j

    Arguments:
        file: file path or file object of the VTK file
        filters: string array, regexes of reaction rate names
    """

    # Parses the XML file and returns root
    tree = ET.parse(file)
    root = tree.getroot()

    # Finds the extent of the mesh and the number of lattice cells
    piece = root.find('.//Piece')
    extent = piece.get('Extent').split(' ')
    num_cells_xy = int(piece.get('NumberOfCellsXY'))

    # Computes the dimensions of the mesh
    nx = int(extent[0])
    ny = int(extent[1])
    nz = int(extent[2])

    print('Mesh dimensions = [%d, %d, %d]' % (nx, ny, nz))
    
    # Initializes a numpy array dictionary
    arrays = {}

    # Gets all of the valid indices
    cell_data = piece.find('CellData')
    valid_indices = []
    for data_array in cell_data.findall('DataArray'):
        data_name = data_array.get('Name')
        if data_name == 'Valid Indices':
            data = data_array.text.split()
            valid_indices = [int(i) for i in data]

    # Processes data arrays one by one
    # This is done by first extract an array of data from a XML node
    # and then write it down to a numpy array
    imported_arrays = []
    skipped_arrays = []
    for data_array in cell_data.findall('DataArray'):
        data_name = data_array.get('Name')

        # Skips unwanted reaction rates
        if filters and len(filters) > 0:
            if sum([1 if re.search(x, data_name) else 0 for x in filters]) == 0:
                skipped_arrays.append(data_name)
                continue
        # If rates are not specified, extract all the arrays
        imported_arrays.append(data_name)

        # Creates a 3D numpy array
        result = np.zeros((nz, ny, nx))

        # Reads reaction rates.
        data = data_array.text.split()

        # Remember that (i,j) is the position in the tally mesh and should
        # be mapped into the Cartesian coordinate system.
        # Iterates z-sections and x-y cells.
        for z in range(nz):
            for count in range(num_cells_xy):
                # Sums up reaction rates along the z-axis
                value = 0.
                lookup_count = count + z * num_cells_xy
                value = float(data[lookup_count])

                # Computes the lattice cell position in the 3D array
                indx = valid_indices[lookup_count]
                x = int(indx % nx)
                y = int(indx // nx % ny)
                j = ny - 1 - y # revert the y-axis
                k = x
                result[z, j, k] = value

        # Saves the array to the numpy array dictionary
        arrays[data_name] = result

    print(f'Imported data array(s): {imported_arrays}')
    print(f'Skipped data array(s): {skipped_arrays}')
    print('Done.')
    return arrays

def normalize(data):
    return data / np.sum(data) * np.count_nonzero(data)