import io
import os
import unittest
from pathlib import Path

import numpy
import rasterio
import xarray
from drb.exceptions.core import DrbNotImplementationException, DrbException
from drb.drivers.file import DrbFileFactory

from drb.drivers.image import DrbImageFactory, DrbImageBaseNode
from drb.drivers.image.simple_node import DrbImageNodesValueNames


class TestDrbTifNode(unittest.TestCase):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))

    image_fake = current_path / "files" / "fake.tiff"
    image_tif_one = current_path / "files" / 'GeogToWGS84GeoKey5.tif'

    image_png = current_path / "files" / 'png-248x300.png'
    image_jp2_no_geo = current_path / "files" / 'relax.jp2'
    node = None
    node_file = None

    def setUp(self) -> None:
        self.node = None
        self.node_file = None

    def tearDown(self) -> None:
        if self.node is not None:
            self.node.close()
        if self.node_file is not None:
            self.node_file.close()

    def open_node(self, path_file):
        self.node_file = DrbFileFactory().create(path_file)
        self.node = DrbImageFactory().create(self.node_file)
        return self.node

    def test_format_name(self):
        root_node = self.open_node(str(self.image_tif_one))

        self.assertIsInstance(root_node, DrbImageBaseNode)
        self.assertIsNone(root_node.namespace_uri)

        node_value = root_node[DrbImageNodesValueNames.FORMAT.value]
        self.assertIsNotNone(node_value)
        self.assertEqual(node_value.value, 'GTiff')
        root_node.close()

    def test_shape(self):
        root_node = self.open_node(str(self.image_png))

        node_value = root_node[DrbImageNodesValueNames.WIDTH.value]
        self.assertIsNotNone(node_value)
        self.assertEqual(node_value.value, 248)

        node_value = root_node[DrbImageNodesValueNames.HEIGHT.value]

        self.assertIsNotNone(node_value)
        self.assertEqual(node_value.value, 300)
        root_node.close()

    def test_type_band_count(self):
        root_node = self.open_node(str(self.image_tif_one))

        node_value = root_node[DrbImageNodesValueNames.TYPE.value]
        self.assertIsNotNone(node_value)
        self.assertEqual(node_value.value, 'uint8')

        node_value = root_node[DrbImageNodesValueNames.NUM_BANDS.value]
        self.assertIsNotNone(node_value)
        self.assertEqual(node_value.value, 1)
        root_node.close()

    def test_image_attributes(self):
        root_node = self.open_node(str(self.image_tif_one))

        list_attributes = root_node.attributes

        self.assertEqual(len(list_attributes), len(self.node_file.attributes))

        with self.assertRaises(KeyError):
            list_attributes[('phase_fitting_1', 'test')]
        with self.assertRaises(DrbException):
            root_node.get_attribute('test', None)
        root_node.close()

    def test_image_parent(self):
        root_node = self.open_node(str(self.image_tif_one))

        self.assertEqual(root_node.parent, self.node_file.parent)
        level1 = root_node[0]

        self.assertEqual(level1.parent, root_node)
        root_node.close()

    def test_image_value(self):
        root_node = self.open_node(str(self.image_tif_one))

        self.assertIsNone(root_node.value)
        root_node.close()

    def test_image_impl(self):
        root_node = self.open_node(str(self.image_tif_one))

        self.assertTrue(root_node.has_impl(rasterio.DatasetReader))

        impl = root_node.get_impl(rasterio.DatasetReader)

        self.assertIsInstance(impl, rasterio.DatasetReader)
        read = impl.read()

        self.assertIsInstance(read, numpy.ndarray)

        impl_numpy = root_node.get_impl(numpy.ndarray)
        self.assertIsInstance(impl_numpy, numpy.ndarray)

        root_node.close()
        impl.close()

    def test_image_impl_not_supported(self):
        root_node = self.open_node(str(self.image_tif_one))

        self.assertFalse(root_node.has_impl(io.BufferedRandom))

        with self.assertRaises(DrbNotImplementationException):
            root_node.get_impl(io.BufferedRandom)
        root_node.close()

    def test_image_with_crs(self):
        root_node = self.open_node(str(self.image_tif_one))

        crs_node = root_node[DrbImageNodesValueNames.CRS.value]
        self.assertIsNotNone(crs_node)

        self.assertIsNotNone(crs_node.value)

        self.assertIsNotNone(rasterio.crs.CRS.from_dict(crs_node
                                                        .value.to_dict()))

        crs_node.close()
        root_node.close()

    def test_image_without_crs(self):
        root_node = self.open_node(str(self.image_png))

        crs_node = root_node[DrbImageNodesValueNames.CRS.value]
        self.assertIsNotNone(crs_node)

        self.assertIsNone(crs_node.value)

        crs_node.close()
        root_node.close()

    def test_image_3_bands(self):
        root_node = self.open_node(str(self.image_jp2_no_geo))

        num_bands_node = root_node[DrbImageNodesValueNames.NUM_BANDS.value]
        self.assertIsNotNone(num_bands_node)

        self.assertEqual(num_bands_node.value, 3)

        root_node.close()

    def test_image_unknown_tags(self):
        root_node = self.open_node(str(self.image_png))

        fake_dict = {
            'width': 140,
            'height': 180
        }
        self.assertTrue(root_node.has_child())
        root_node._add_node_value_from_dict('Format1', fake_dict, 'driver')
        format1_node = root_node['Format1']
        self.assertIsNone(format1_node.value)

        root_node.close()

    def test_image_impl_xarray(self):
        root_node = self.open_node(str(self.image_tif_one))

        self.assertTrue(root_node.has_impl(rasterio.DatasetReader))

        impl = root_node.get_impl(xarray.DataArray)

        self.assertIsInstance(impl, xarray.DataArray)

        self.assertEqual(len(impl.coords['band']), 1)
        self.assertEqual(len(impl.x), 101)
        self.assertEqual(len(impl.y), 101)

        root_node.close()
        impl.close()

    def test_image_impl_xarray_and_rasterio_togehter(self):
        root_node = self.open_node(str(self.image_tif_one))

        self.assertTrue(root_node.has_impl(rasterio.DatasetReader))

        impl = root_node.get_impl(xarray.DataArray)

        self.assertIsInstance(impl, xarray.DataArray)

        array_data = impl.data
        self.assertIsInstance(array_data, numpy.ndarray)

        impl_numpy = root_node.get_impl(numpy.ndarray)
        self.assertIsInstance(impl_numpy, numpy.ndarray)

        self.assertListEqual(list(array_data[0][10]), list(impl_numpy[0][10]))

        root_node.close()
        impl.close()
