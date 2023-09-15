# Litto3dNode Implementation

This drb-driver-litto3d module implements access to litto3d format (.asc and .xyz files) with DRB data model.
It is able to retrieve common implementations such as pandas, numpy or rasterio.

## litto3d Factory and litto3d Node

The module implements the basic factory model defined in DRB in its node resolver. Based on the python entry point mechanism, this module can be dynamically imported into applications.

The entry point group reference is `drb.driver`.<br/>
The implementation name is `litto3d`.<br/>
The factory class is encoded into `drb.drivers.litto3d.node`.<br/>

The litto3d has 2 formats:

- .asc which contains a header with spatial attributes and array attributes and an array of data
- .xyz which contains a list of coordinates and the z value with some metadata about the litto3D

The base node can be a DrbFileNode, DrbHttpNode, DrbZipNode or any other nodes able to provide streamed (`BufferedIOBase`, `RawIOBase`, `IO`) litto3d content.

## limitations

The current version does not manage child modification and insertion. litto3dNode is currently read only.

## Using this module

To include this module into your project, the `drb-driver-litto3d` module shall be referenced into `requirements.txt` file, or the following pip line can be run:

```commandline
pip install drb-driver-litto3d
```
