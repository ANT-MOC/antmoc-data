antmoc-mgxs
===========

Packages for multi-group cross-section manipulation.

These packages provide tools for checking, manipulating, and generating MGXS files for ANT-MOC.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Install](#install)
- [Examples](#examples)
- [HDF5 Data Layout](#hdf5-data-layout)
  - [Layout: named](#layout-named)
  - [Layout: compact/compressed](#layout-compactcompressed)
- [Common Modules](#common-modules)
- [Type A](#type-a)
    - [Modules](#modules)
    - [File Formats](#file-formats)
- [Type B](#type-b)
    - [Modules](#modules-1)
    - [File Formats](#file-formats-1)
- [License](#license)


## Prerequisites

- Python >= 3.6
- numpy
- h5py

## Install

Download the source to your disk, change to the source directory, and simply run pip to install the package.

```bash
$ pip install .
```

After installation, a package named `antmoc-mgxs` will be available, which has several sub-packages.

## Examples

Check the directory `examples/` for illustrations on how to use `antmoc-mgxs`.

Each of the sample scripts accepts command line arguments.

```bash
./examples/h5/fix_materials.py --help
./examples/xml/fix_materials_in_xml.py --help
```

## HDF5 Data Layout

There are two layouts of material data in an H5 file. Materials are treated as data groups in both of the layouts.

In addition to materials, the H5 file must contain a top-level attribute named '# groups' for the number of energy groups.

### Layout: named

This is the default cross-section data layout for ANT-MOC.

Cross-section arrays are stored in H5 datasets individually. In this layout, a group for a material consists of several datasets:

- `absorption`
- `fission`
- `nu-fission`
- `transport`, or `total`
- `chi`
- `scatter matrix`, or `nu-scatter matrix`, or `consistent scatter matrix`

For example, a simple cross-section file could have the following hierarchy

```
attribute  "# groups"
group      /
group      /material/MOX-8.7%
dataset    /material/MOX-8.7%/chi
dataset    /material/MOX-8.7%/fission
dataset    /material/MOX-8.7%/nu-fission
dataset    /material/MOX-8.7%/scatter matrix
dataset    /material/MOX-8.7%/total
group      /material/UO2
dataset    /material/UO2/chi
dataset    /material/UO2/fission
dataset    /material/UO2/nu-fission
dataset    /material/UO2/scatter matrix
dataset    /material/UO2/total
```

The scatter matrix is usually a flattened n-by-n matrix, where n is the number of energy groups.
Elements in the scatter dataset respect the *source-major* order, which is much like the row-major order.

For example, a scatter matrix with 2 energy groups has 4 elements, which are stored as

```
1->1
1->2
2->1
2->2
```

> The number before symbol `->` is the source group, and the number after the symbol is the destination group.

### Layout: compact/compressed

TODO

## Common Modules

- `material`: class `Material` representing cross-sections. A material object could be written to an HDF5 file as a dataset.
- `materialxml`: representation for the XML material definition, which is used to handle `materials.xml`.
- `manip`: data manipulation utilities.
- `options`: representation of command line options.

## Type A

Package `antmoc-mgxs.type_a` defines a generator which accepts two files to create an mgxs input for antmoc:

- `infilecross`: cross-sections in plain text.
- `materials.xml`: material definitions in XML, including nuclear densities.

### Modules

- `material`: definition of `MaterialTypeA`, which is a sub-class of `Material`.
- `nuclides`: representations of nuclides and nuclide sets, which are basically defined in a plain text file called "infilecross".
- `infilecross`: functions for parsing an "infilecross" file. The file must be well-formed.
- `generate`: functions for mgxs generation.
- `options`: definition of `OptionsTypeA`, which is a sub-class of `Options`.

### File Formats

#### `materials.xml`

This is an XML file consisting of material definitions.

```xml
<?xml version="1.0" encoding="utf-8"?>
<MATERIAL>
    <material name="1" set="1" density="0.0E+00" temperature="523.15K" label="Some material">
        <nuclide id="1102301" radio="1.6098e-2"/>
        <nuclide id="601201"  radio="7.3771e-5"/>
    </material>
</MATERIAL>
```

- `material`: definition of a material object.
- `material.name`: material name which will be written into the H5 file (string).
- `material.set`: nuclide set ID for MGXS calculations (int, defaults to `name`).
- `material.label`: a short description.
- `nuclide`: nuclide information for MGXS calculations.
- `nuclide.id`: nuclide ID containing its atomic number and mass (int).
- `nuclide.radio`: density used by MGXS calculations (float).

#### `infilecross`

This is a plain text file consisting of nuclide set definitions.

```
$SOMESTRING 1  7SETs 1SET
   2  30   6   5   0   0
  0.57564402E+00  0.29341474E+00  0.12731624E+00 ...
  ...
  2511102302   0   3   6SODIUM-23
  ...
  4311402802   0   3   6SILICON-28
  ...
$SOMESTRING 1  7SETs SET2
  ...
```

## Type B

TODO

### Modules

### File Formats

## License

MIT
