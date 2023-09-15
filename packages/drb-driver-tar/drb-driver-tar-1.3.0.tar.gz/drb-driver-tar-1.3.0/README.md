# TarNode Implementation

This drb-driver-tar module implements access to tar containers with DRB data model. It is able to navigates among the tar contents.

## Tar Factory and Tar Node

The module implements the basic factory model defined in DRB in its node resolver. Based on the python entry point mechanism, this module can be dynamically imported into applications.

The entry point group reference is `drb.driver`.<br/>
The implementation name is `tar`.<br/>
The factory class is encoded into `drb.drivers.tar.base_node`.<br/>

The tar factory creates a TarNode from an existing tar content. It uses a base node to access the content data using a streamed implementation from the base node.

The base node can be a DrbFileNode, DrbHttpNode, DrbZipNode or any other nodes able to provide streamed (`BufferedIOBase`, `RawIOBase`, `IO`) tar content.

## limitations

The current version does not manage child modification and insertion. TarNode is currently read only.

## Using this module

To include this module into your project, the `drb-driver-tar` module shall be referenced into `requirements.txt` file, or the following pip line can be run:

```commandline
pip install drb-driver-tar
```
