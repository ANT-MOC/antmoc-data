ANT-MOC Data
===========

A package for ANT-MOC data manipulation.

- [ANT-MOC Data](#ant-moc-data)
  - [Prerequisites](#prerequisites)
  - [Install](#install)
  - [License](#license)
  - [Subpackage: ANT-MOC Solution](#subpackage-ant-moc-solution)
    - [Load data to numpy arrays](#load-data-to-numpy-arrays)
  - [Subpackage: ANT-MOC Log](#subpackage-ant-moc-log)
    - [Examples](#examples)
    - [Log file](#log-file)
    - [Extractor](#extractor)
    - [Fields](#fields)
    - [Save log database](#save-log-database)
  - [Subpackage: ANT-MOC MGXS](#subpackage-ant-moc-mgxs)
    - [Examples](#examples-1)
    - [HDF5 data layout](#hdf5-data-layout)
      - [Layout: named](#layout-named)
      - [Layout: compact/compressed](#layout-compactcompressed)
    - [Common modules](#common-modules)
    - [Type A](#type-a)
      - [Modules](#modules)
      - [File formats](#file-formats)
        - [`materials.xml`](#materialsxml)
        - [`infilecross`](#infilecross)
    - [Type B](#type-b)
      - [Modules](#modules-1)
      - [File formats](#file-formats-1)

## Prerequisites

- Python >= 3.8
- baseopt
- numpy
- h5py

## Install

```bash
$ pip install antmocdata
```

## License

MIT

## Subpackage: ANT-MOC Solution

Package `antmocdata.solution` provides tools for processing reaction rates and fluxes produced by ANT-MOC.

### Load data to numpy arrays

Function `antmocdata.solution.load_vtu` reads reaction rates and fluxes from a `.vtu` file and stores them in a dictionary of numpy arrays.

```python
from antmocdata.solution import load_vtu
# Read only the 'Avg Fission RX' dataset from file 'reaction_rates.vtu'
rx = load_vtu("reaction_rates.vtu", ["^Avg Fission RX$"])
fiss = rx["Avg Fission RX"]
print(fiss.shape)
```

For ANT-MOC v0.1.15, a reaction rate dataset in a `.vtu` file is a 1D array.
If the dimensions of reaction rate distributions are `(Nx, Ny, Nz)`, a data point `(x,y,z)` is indexed by `x+y*Nx+z*Nx*Ny` in the dataset.

Loading the file with `load_vtu` will revert the y-axis. Back to the previous example, loaded data can be accessed by `fiss[z, y, x]`.

<img src="https://github.com/ANT-MOC/antmoc-data/assets/22237751/74fe69d2-c758-4f53-81ca-939a37305417" height="300">

## Subpackage: ANT-MOC Log

Package `antmocdata.log` provides tools for exploring ANT-MOC logs.

### Examples

Please check the directory `examples/log` for live examples.

Each of the sample scripts accepts command line arguments.

```bash
python ./examples/log/extract-records.py --help
```

### Log file

A log file of ANT-MOC contains many data fields. A group of log files are managed by the `LogDB` object. By default, the `LogDB` object only keeps log file paths. Each of the log files won't be read and serialized until it is queried.

```python
from antmocdata.log import Options, LogDB
options = Options()
# ...
# setup options eigher through CLI or direct assignments
# ...
# Singleton
logdb = LogDB()
logdb.setup(options)
```

To avoid parsing the samke log files repeatedly, one can set the `LogDB` object to the caching mode or explicitly load all the log files.

```python
logdb.cache = True # caching mode
logdb.cache_all() # load all the logs immediately
```

### Extractor

A log extractor is used to make `LogDB` queries and save the results to a `.csv` file. For example, to get log files with specific fields, one could write down

```python
options["output"].value = "antmoc-records.csv"
options["specs"].value = ["Azims", "Polars"]
extractor = TinyExtractor(logdb)
extractor.extract()
```

This would list the `Azims` and `Polars` fields of all the log files and save the results to `antmoc-records.csv`.

In this case, `Azims` and `Polars` are called `FieldSpec`. A spec can be used to filter out results. For example,

```python
# List Azims and Polars fields of all the logs
options["specs"].value = ["Azims", "Polars"]
# List Azims and Polars fields of all the logs, and
# only show logs with Azims=64 
options["specs"].value = ["Azims=64", "Polars"]
# List Azims and Polars fields of all the logs, and
# only show logs with Azims=64 and Polars>2
options["specs"].value = ["Azims=64", "Polars>2"]
extractor.extract()
```

A `FieldSpec` consists of three parts: field name, binary operator, and value. Perl regex is supported for the field name and the operator. For example, `".*Time"` could match all the fields with an ending `Time` string.

The binary operator could be `==`, `<`, `<=`, `>`, or `>=`. Operator `==` is for string comparison and perl regex is supported in this case. Inequality symbols are for string or numerical comparisons.

> Be careful if you want to use inequality symbols on string fields. Values from these fields are compared through string comparison. Predefined field types are located in `antmocdata.log.default_fields.json`.

### Fields

Predefined log fields are located in `antmocdata.log.default_fields.json`. If these fields are outdated due to ANT-MOC updates, please update this json file or load a new one in your scripts.

```python
from antmocdata.log import fields
fields.load("path/to/your/fields.json")
```

There is also an `add` method for appending single field to the field dictionary.

```python
from antmocdata.log import Field
fields.add(Field(name="NewField1", patterns=["NewField1.*"]))

# or adding the field directly to LogFields
from antmocdata.log import LogFields
LogFields().add(Field(name="NewField2", patterns=["NewField2.*"]))
```

### Save log database

A `LogDB` object can be dumped as json files to a specific directory.

```python
options["savedb"].value = "antmoc-logdb/"
# ...
# setup the LogDB object
# ...
logdb.save(options("savedb"))
```

## Subpackage: ANT-MOC MGXS

Package `antmocdata.mgxs` provides tools for checking, manipulating, and generating MGXS files for ANT-MOC.

### Examples

Please check the directory `examples/mgxs` for live examples.

Each of the sample scripts accepts command line arguments.

```bash
python ./examples/mgxs/h5/fix-materials.py --help
python ./examples/mgxs/xml/fix-materials-in-xml.py --help
```

### HDF5 data layout

There are two layouts of material data in an H5 file. Materials are treated as data groups in both of the layouts.

In addition to materials, the H5 file must contain a top-level attribute named '# groups' for the number of energy groups.

#### Layout: named

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

#### Layout: compact/compressed

TODO

### Common modules

- `material`: class `Material` representing cross-sections. A material object could be written to an HDF5 file as a dataset.
- `materialxml`: representation for the XML material definition, which is used to handle `materials.xml`.
- `manip`: data manipulation utilities.
- `options`: representation of command line options.

### Type A

Package `antmocdata.mgxs.type_a` defines a generator which accepts two files to create an mgxs input for antmoc:

- `infilecross`: cross-sections in plain text.
- `materials.xml`: material definitions in XML, including nuclear densities.

#### Modules

- `material`: definition of `MaterialTypeA`, which is a sub-class of `Material`.
- `nuclides`: representations of nuclides and nuclide sets, which are basically defined in a plain text file called "infilecross".
- `infilecross`: functions for parsing an "infilecross" file. The file must be well-formed.
- `generate`: functions for mgxs generation.
- `options`: definition of `OptionsTypeA`, which is a sub-class of `Options`.

#### File formats

##### `materials.xml`

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

##### `infilecross`

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

### Type B

TODO

#### Modules

#### File formats
