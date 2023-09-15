import os
import unittest
from pathlib import Path
import io

from drb.drivers.file import DrbFileFactory

from drb.drivers.image import DrbImageFactory, DrbImageBaseNode
from drb.drivers.image.simple_node import DrbImageNodesValueNames

IMAGE = DrbImageNodesValueNames.IMAGE.value


class TestDrbNodeFactoryNetcdf(unittest.TestCase):
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

    def test_opened_file_node(self):
        node = self.open_node(str(self.image_tif_one))

        self.assertIsInstance(node, DrbImageBaseNode)
        self.assertEqual(node.name, self.node_file.name)
        self.assertEqual(node.namespace_uri, self.node_file.namespace_uri)

    def test_base_node(self):
        node = self.open_node(str(self.image_tif_one))

        self.assertEqual(node.parent, self.node_file.parent)
        self.assertEqual(node.value, self.node_file.value)

        self.assertIsInstance(node, DrbImageBaseNode)

        self.assertEqual(len(node), 8)
        self.assertTrue(node.has_child())
        self.assertEqual(len(node.children), 8)

    def test_base_node_attribute(self):
        node = self.open_node(str(self.image_tif_one))

        self.assertEqual(node.attributes, self.node_file.attributes)
        self.assertEqual(node.get_attribute('mode'),
                         self.node_file.get_attribute(
                             'mode'))

    def test_base_node_impl(self):
        node = self.open_node(str(self.image_tif_one))

        impl_base_file = io.BufferedIOBase

        self.assertTrue(node.has_impl(impl_base_file))

        impl = node.get_impl(impl_base_file)
        self.assertIsNotNone(impl)
        self.assertIsInstance(impl, impl_base_file)
        impl.close()

    def test_first_group(self):
        node = self.open_node(str(self.image_tif_one))

        self.assertIsInstance(node, DrbImageBaseNode)
        root_node = node[0]
        self.assertIsNotNone(root_node)
        root_node.close()
