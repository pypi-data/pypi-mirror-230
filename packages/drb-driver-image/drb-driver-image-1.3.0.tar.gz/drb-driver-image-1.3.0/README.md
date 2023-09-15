# ImageNode Implementation
This drb-driver-image module implements images data formats to be accessed with DRB data model. It is able to navigates among the images contents and accessing the image data.

### Supported images formats
The current implementation is based on RasterIO module. It has been tested with Tiff/GeoTIFF, Jp2k and png formats.

There are no limitations to use other formats supported by rasterio, see
https://gdal.org/drivers/raster/index.html for details.

## Image Factory and Image Node
The module implements the basic factory model defined in DRB in its node resolver. Based on the python entry point mechanism, this module can be dynamically imported into applications.

The entry point group reference is `drb.drivers`.<br/>
The implementation name is `image`.<br/>
The factory class is encoded into `drb-drivers-image.base_node`.<br/>

The image factory creates an ImageNode from an existing image data. It uses a base node to access the content data with the streamed base node implementation.

The base node can be a FileNode (See drb-driver-file), HttpNode, ZipNode or any other node able to provide streamed (`BufferedIOBase`, `RawIOBase`, `IO`) xml content.
## limitations
The current version does not manage child modification and insertion. ImageNode is currently read only.
## Using this module
To include this module into your project, the `drb-driver-image` module shall be referenced into `requirement.txt` file, or the following pip line can be run:
```commandline
pip install drb-driver-image
```
