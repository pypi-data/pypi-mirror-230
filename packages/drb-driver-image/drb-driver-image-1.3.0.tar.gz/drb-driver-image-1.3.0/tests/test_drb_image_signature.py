import os
import sys
import unittest
import uuid
from pathlib import Path

from drb.core.factory import FactoryLoader
from drb.nodes.logical_node import DrbLogicalNode
from drb.topics.dao import ManagerDao
from drb.topics.topic import TopicCategory

from drb.drivers.image import DrbImageFactory


class TestDrbImageSignature(unittest.TestCase):
    fc_loader = None
    topic_loader = None
    file_id = uuid.UUID('b7e03ac0-2b62-11ec-8d3d-0242ac130003')
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))
    image_tif_one = current_path / "files" / 'GeogToWGS84GeoKey5.tif'
    image_png = current_path / "files" / 'png-248x300.png'
    image_jp2 = current_path / "files" / 'relax.jp2'
    empty_file = current_path / "files" / 'empty_file'

    @classmethod
    def setUpClass(cls) -> None:
        cls.fc_loader = FactoryLoader()
        cls.topic_loader = ManagerDao()

    def test_impl_loading(self):
        factory_name = 'image'

        factory = self.fc_loader.get_factory(factory_name)
        self.assertIsNotNone(factory)
        self.assertIsInstance(factory, DrbImageFactory)

        topic = self.topic_loader.get_drb_topic(self.file_id)
        self.assertIsNotNone(factory)
        self.assertEqual(self.file_id, topic.id)
        self.assertEqual('image', topic.label)
        self.assertIsNone(topic.description)
        self.assertEqual(TopicCategory.FORMATTING, topic.category)
        self.assertEqual(factory_name, topic.factory)

    def test_impl_signatures(self):
        topic = self.topic_loader.get_drb_topic(self.file_id)

        node = DrbLogicalNode(self.image_tif_one)
        self.assertTrue(topic.matches(node))

        node = DrbLogicalNode(self.image_png)
        self.assertTrue(topic.matches(node))

        node = DrbLogicalNode(self.image_jp2)
        self.assertTrue(topic.matches(node))

        node = DrbLogicalNode('https://gitlab.com/drb-python')
        self.assertFalse(topic.matches(node))
