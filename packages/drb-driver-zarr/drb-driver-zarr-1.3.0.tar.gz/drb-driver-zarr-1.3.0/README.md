# ZarrNode Driver

This drb-driver-zarr module implements access to zarr containers with DRB data model. It is able to navigates among the zarr contents.

## Zar Factory and Zarr Node

The module implements the basic factory model defined in DRB in its node resolver. Based on the python entry point mechanism, this module can be dynamically imported into applications.

The entry point group reference is `drb.driver`.<br/>
The driver name is `zarr`.<br/>
The factory class is decribed with implementation `drb.drivers.zarr.zarr_node_factory`.<br/>

The zarr factory creates a ZarrNode from an existing zarr content. It uses a base node to access the content data using a streamed implementation from the base node.

The base node can be a DrbFileNode, DrbHttpNode, DrbTarNode or any other nodes able to provide streamed (`BufferedIOBase`, `RawIOBase`, `IO`) zarr content.

## limitations

The current version does not manage child modification and insertion. ZarrNode is currently read only.

## Using this module

To include this module into your project, the `drb-driver-zarr` module shall be referenced into `requirements.txt` file, or the following pip line can be run:

```commandline
pip install drb-driver-zarr
```
