# GRIB driver
This drb-driver-grib module implements grib format access with DRB data model. It is able to navigates among the grib contents.

## GRIB Factory and GRIB Node
The module implements the basic factory model defined in DRB in its node resolver. Based on the python entry point mechanism, this module can be dynamically imported into applications.

The entry point group reference is `drb.driver`.<br/>
The driver name is `grib`.<br/>
The factory class `DrbGribFactory` is encoded into `drb.drivers.factory`
module.<br/>

The GRIB data model containing a set of Attributes, Dimensions; Coordinates and Variables. It also includes User-defined set of types.
The Drb structure implemented here, reproduces this representation.
Attributes are reported in node as node attributes whereas Coordinates, Dimensions and Values are reported as node children. The raw content is available in Variable node requesting array (xarray, or numpy ndarray types)

## limitations
The current version does not manage child modification and insertion. `DrbGribNode` is currently read only.
The factory to build DrbGribNode supports file directly opening it with path, for other implementation ByteIO or BufferedIOBase, they are manged with a local temporary file, removed when the node is closed..

## Using this module
To include this module into your project, the `drb-driver-grib` module shall be referenced into `requirements.txt` file, or the following pip line can be run:
```commandline
pip install drb-driver-grib
```

This module depends on cfgrib

See installation of cfgrib, on https://pypi.org/project/cfgrib/
If you install it by pip install you need to install the ECMWF ecCodes library.
See https://confluence.ecmwf.int/display/ECC/ecCodes+installation.

