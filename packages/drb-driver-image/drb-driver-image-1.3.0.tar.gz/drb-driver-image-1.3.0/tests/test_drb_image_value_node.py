import io
import os
import posixpath
import unittest
from pathlib import Path

import rasterio
from drb.exceptions.core import DrbException
from drb.drivers.file import DrbFileFactory

from drb.drivers.image import DrbImageFactory
from drb.drivers.image.simple_node import DrbImageNodesValueNames

GROUP_NOT_EXIST = "fake_group"


class TestDrbValueNodeImage(unittest.TestCase):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))

    image_fake = current_path / "files" / "fake.tiff"
    image_tif_one = current_path / "files" / 'GeogToWGS84GeoKey5.tif'
    image_png = current_path / "files" / 'png-248x300.png'
    image_jp2 = current_path / "files" / 'relax.jp2'
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

    def test_value_attributes(self):
        root_node = self.open_node(str(self.image_tif_one))

        self.assertIsNone(root_node.namespace_uri)

        node_value = root_node[DrbImageNodesValueNames.FORMAT.value]
        self.assertIsNotNone(node_value)
        self.assertEqual(node_value.value, 'GTiff')
        attributes = node_value.attributes
        self.assertEqual(len(attributes), 0)
        with self.assertRaises(DrbException):
            self.assertIsNotNone(node_value.get_attribute('toto', None))

    def test_value_parent(self):
        root_node = self.open_node(str(self.image_tif_one))

        node_value = root_node[DrbImageNodesValueNames.FORMAT.value]
        self.assertEqual(node_value.parent, root_node)

    def test_value_impl(self):
        root_node = self.open_node(str(self.image_tif_one))

        node_value = root_node[DrbImageNodesValueNames.FORMAT.value]

        self.assertFalse(node_value.has_impl(rasterio.DatasetReader))
        self.assertFalse(node_value.has_impl(io.BufferedIOBase))

        with self.assertRaises(DrbException):
            node_value.get_impl(io.BufferedIOBase)

    def test_variable_namespace_uri(self):
        root_node = self.open_node(str(self.image_tif_one))

        node_value = root_node[DrbImageNodesValueNames.FORMAT.value]
        self.assertIsNone(node_value.namespace_uri)

    def test_variable_get_child_at(self):
        root_node = self.open_node(str(self.image_tif_one))

        node_value = root_node[DrbImageNodesValueNames.FORMAT.value]

        with self.assertRaises(IndexError):
            node_value[-2]
            node_value[0]
        with self.assertRaises(KeyError):
            node_value['Name']

    def test_variable_get_first_last_children(self):
        root_node = self.open_node(str(self.image_tif_one))

        node_value = root_node[DrbImageNodesValueNames.FORMAT.value]

        self.assertEqual(len(node_value), 0)
        self.assertEqual(node_value.children, [])
        self.assertFalse(node_value.has_child())

    def test_path(self):
        root_node = self.open_node(str(self.image_tif_one))

        node_value = root_node[DrbImageNodesValueNames.FORMAT.value]

        self.assertEqual(
            node_value.path.path,
            Path(self.image_tif_one).
            joinpath(DrbImageNodesValueNames.FORMAT.value).as_posix()
            )
