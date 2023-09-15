import os
import unittest
import uuid
from pathlib import Path

from drb.core.factory import FactoryLoader
from drb.topics.dao import ManagerDao
from drb.topics.topic import TopicCategory

from drb.drivers.litto3d import DrbLitto3dFactory
from drb.nodes.logical_node import DrbLogicalNode


class TestDrbLitto3dSignature(unittest.TestCase):
    mock_pkg = None
    fc_loader = None
    topic_loader = None
    litto_id = uuid.UUID("ce5c2275-bba7-4ec4-8ca9-df4cf574fb26")
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))

    asc_file = current_path / "files" / "test_asc.asc"
    xyz_file = current_path / "files" / "test_xyz.xyz"
    empty_file = current_path / "files" / "empty.file"

    @classmethod
    def setUpClass(cls) -> None:
        cls.fc_loader = FactoryLoader()
        cls.topic_loader = ManagerDao()

    def test_driver_loading(self):
        factory_name = "litto3d"
        factory = self.fc_loader.get_factory(factory_name)
        self.assertIsNotNone(factory)
        self.assertIsInstance(factory, DrbLitto3dFactory)

        topic = self.topic_loader.get_drb_topic(self.litto_id)
        self.assertEqual(self.litto_id, topic.id)
        self.assertEqual("Litto3D", topic.label)
        self.assertIsNone(topic.description)
        self.assertEqual(TopicCategory.FORMATTING, topic.category)
        self.assertEqual(factory_name, topic.factory)

    def test_driver_signatures(self):
        topic = self.topic_loader.get_drb_topic(self.litto_id)

        node = DrbLogicalNode(self.asc_file)
        self.assertTrue(topic.matches(node))

        node = DrbLogicalNode(self.xyz_file)
        self.assertTrue(topic.matches(node))

        node = DrbLogicalNode(self.empty_file)
        self.assertFalse(topic.matches(node))
