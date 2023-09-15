import os
import unittest
from pathlib import Path

import numpy
import rasterio
from drb.drivers.file import DrbFileFactory

from drb.drivers.image import DrbImageFactory
from drb.drivers.image.simple_node import DrbImageNodesValueNames

IMAGE = DrbImageNodesValueNames.IMAGE.value


class TestDrbTifNode(unittest.TestCase):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))

    # image_cog = current_path / "files" / "cog.tif"
    image_jpeg = current_path / "files" / "sample_640×426.jpeg"
    image_gif = current_path / "files" / "file_example_GIF_500kB.gif"
    image_webp = current_path / "files" / "file_example_WEBP_50kB.webp"
    image_bmp = current_path / "files" / "w3c_home_256.bmp"
    image_blx = current_path / "files" / "s4103.blx"
    image_bsb = current_path / "files" / "australia4c.kap"
    image_dted = current_path / "files" / "n43_wgs72.dt0"
    image_elas = current_path / "files" / "byte_elas.bin"
    image_gpkg = current_path / "files" / "byte.gpkg"
    image_kakadu = current_path / "files" / "rgbwcmyk01_YeGeo_kakadu.jp2"
    image_jdem = current_path / "files" / "fakejdem.mem"

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

    def open_image_check_dim_and_impl(self, path_file, width_waited,
                                      height_waited):
        root_node = self.open_node(str(path_file))

        self.assertTrue(root_node.has_impl(rasterio.DatasetReader))

        impl = root_node.get_impl(rasterio.DatasetReader)

        self.assertEqual(root_node['width'].value, width_waited)
        self.assertEqual(root_node['height'].value, height_waited)

        self.assertIsInstance(impl, rasterio.DatasetReader)
        read = impl.read()

        self.assertIsInstance(read, numpy.ndarray)

        impl_numpy = root_node.get_impl(numpy.ndarray)
        self.assertIsInstance(impl_numpy, numpy.ndarray)

        root_node.close()
        impl.close()

    # def test_image_cog_impl(self):
    #     self.open_image_check_dim_and_impl(self.image_cog, 16563, 16191)

    def test_image_jpeg_impl(self):
        self.open_image_check_dim_and_impl(self.image_jpeg, 640, 426)

    def test_image_gif_impl(self):
        self.open_image_check_dim_and_impl(self.image_gif, 1900, 1267)

    def test_image_webp_impl(self):
        self.open_image_check_dim_and_impl(self.image_webp, 1050, 700)

    def test_image_bmp_impl(self):
        self.open_image_check_dim_and_impl(self.image_bmp, 72, 48)

    def test_image_blx_impl(self):
        self.open_image_check_dim_and_impl(self.image_blx, 512, 512)

    def test_image_bsb_impl(self):
        self.open_image_check_dim_and_impl(self.image_bsb, 625, 480)

    def test_image_dted_impl(self):
        self.open_image_check_dim_and_impl(self.image_dted, 121, 121)

    def test_image_elas_impl(self):
        self.open_image_check_dim_and_impl(self.image_elas, 20, 20)

    def test_image_GPKG_impl(self):
        self.open_image_check_dim_and_impl(self.image_gpkg, 20, 20)

    def test_image_kakadu_impl(self):
        self.open_image_check_dim_and_impl(self.image_kakadu, 800, 100)

    def test_image_jdem_impl(self):
        self.open_image_check_dim_and_impl(self.image_jdem, 2, 2)
