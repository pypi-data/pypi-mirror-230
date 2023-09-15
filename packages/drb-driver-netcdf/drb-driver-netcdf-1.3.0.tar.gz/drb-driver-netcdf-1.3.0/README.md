# Netcdf driver
This drb-driver-netcdf module implements netcdf format access with DRB data model. It is able to navigates among the netcdf contents.

## Netcdf Factory and Netcdf Node
The module implements the basic factory model defined in DRB in its node resolver. Based on the python entry point mechanism, this module can be dynamically imported into applications.

The entry point group reference is `drb.driver`.<br/>
The driver name is `netcdf`.<br/>
The factory class `DrbNetcdfFactory` is encoded into `drb.drivers.factory`
module.<br/>


The netCDF 4.0 data model is based on recursive structure of Groups each containing a set of Attributes, Dimensions and Variables. It also includes User-defined set of types.
The Drb structure implemented here, reproduces this representation.
Attributes are reported in node as node attributes whereas Dimensions and Values are reported as node children. The raw content is available in Variable node requesting array (xarray, or numpy ndarray types)

## limitations
The current version does not manage child modification and insertion. `DrbNetcdfNode` is currently read only.
The factory to build DrbNetcdfNode supports file directly opening it with path, for other implementation ByteIO or BufferedIOBase, they are manged with a local temporary file, removed when the node is closed..

## limitations HDF-EOS file
When open a HDF-EOS file in HDF4 format
If fails with message:`[Errno -128] NetCDF: Attempt to use feature that was not turned on when netCDF was built`
This means that NetCDF system library linked with netCDF4 python wasn't compiled with HDF4 support.
You can try to install netCDF4 python by conda
```commandline
conda install -c conda-forge netcdf4
```
Or rebuild netCDF4 locally with netCDF library with support hdf4 turned ON

## Using this module
To include this module into your project, the `drb-driver-netcdf` module shall be referenced into `requirements.txt` file, or the following pip line can be run:
```commandline
pip install drb-driver-netcdf
```


