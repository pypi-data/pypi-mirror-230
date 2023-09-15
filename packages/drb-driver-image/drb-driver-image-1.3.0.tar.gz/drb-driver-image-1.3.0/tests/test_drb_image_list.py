import os
import io
import posixpath
import unittest
from pathlib import Path

import numpy
import drb
from drb.exceptions.core import DrbNotImplementationException, DrbException
from drb.drivers.file import DrbFileFactory

from drb.drivers.image import DrbImageFactory
from drb.drivers.image.simple_node import DrbImageNodesValueNames


class TestDrbListNodeImage(unittest.TestCase):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))

    image_fake = current_path / "files" / "fake.tiff"
    image_tif_one = current_path / "files" / 'GeogToWGS84GeoKey5.tif'
    image_png = current_path / "files" / 'png-248x300.png'
    image_jp2 = current_path / "files" / 'relax.jp2'

    def test_list_children(self):
        node_file = DrbFileFactory().create(str(self.image_tif_one))

        root_node = DrbImageFactory().create(node_file)

        tags_list = root_node[DrbImageNodesValueNames.META.value]

        self.assertTrue(tags_list.has_child())
        self.assertIsNotNone(tags_list['transform'])

        self.assertIsNotNone(tags_list[-1])
        root_node.close()

    def test_list_parent(self):
        node_file = DrbFileFactory().create(str(self.image_tif_one))
        root_node = DrbImageFactory().create(node_file)

        tags_list = root_node[DrbImageNodesValueNames.TAGS.value]
        self.assertEqual(tags_list.parent, root_node)
        self.assertEqual(tags_list.name, DrbImageNodesValueNames.TAGS.value)

        root_node.close()

    def test_list_namespace_uri(self):
        node_file = DrbFileFactory().create(str(self.image_tif_one))

        root_node = DrbImageFactory().create(node_file)

        tags_list = root_node[DrbImageNodesValueNames.TAGS.value][0]
        self.assertIsNone(tags_list.namespace_uri)
        root_node.close()

    def test_list_value(self):
        node_file = DrbFileFactory().create(str(self.image_tif_one))

        root_node = DrbImageFactory().create(node_file)

        tags_list = root_node[DrbImageNodesValueNames.TAGS.value]

        self.assertIsNone(tags_list.value)
        root_node.close()

    def test_list_impl_not_supported(self):
        node_file = DrbFileFactory().create(str(self.image_tif_one))

        root_node = DrbImageFactory().create(node_file)

        tags_list = root_node[DrbImageNodesValueNames.TAGS.value]

        self.assertFalse(tags_list.has_impl(io.BufferedIOBase))
        self.assertFalse(tags_list.has_impl(numpy.ndarray))

        with self.assertRaises(DrbNotImplementationException):
            tags_list.get_impl(io.BufferedIOBase)
        root_node.close()

    def test_list_no_attributes(self):
        node_file = DrbFileFactory().create(str(self.image_tif_one))

        root_node = DrbImageFactory().create(node_file)

        tags_list = root_node[DrbImageNodesValueNames.TAGS.value]
        self.assertFalse(bool(tags_list.attributes))
        with self.assertRaises(DrbException):
            tags_list.get_attribute('toto', None)
        root_node.close()

    def test_path(self):
        node_file = DrbFileFactory().create(str(self.image_tif_one))

        root_node = DrbImageFactory().create(node_file)

        tags_list = root_node[DrbImageNodesValueNames.META.value]

        self.assertEqual(
            tags_list.path.path,
            Path(self.image_tif_one).
            joinpath(DrbImageNodesValueNames.META.value).as_posix()
        )

        root_node.close()
        node_file.close()
