import os
import sys
import unittest
import uuid
from pathlib import Path

from drb.core.factory import FactoryLoader
from drb.nodes.logical_node import DrbLogicalNode
from drb.topics.dao import ManagerDao
from drb.topics.topic import TopicCategory

from drb.drivers.zarr import DrbZarrFactory


class TestDrbZarrSignature(unittest.TestCase):
    mock_pkg = None
    fc_loader = None
    topic_loader = None
    zarr_id = uuid.UUID("56e6509c-3666-11ec-8d3d-0242ac130003")
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))

    zarr_ok2 = current_path / "files" / "sample.zarr"
    not_zarr_files = current_path / "files" / "empty.file"

    @classmethod
    def setUpClass(cls) -> None:
        cls.fc_loader = FactoryLoader()
        cls.topic_loader = ManagerDao()

    def test_impl_loading(self):
        factory_name = "zarr"

        factory = self.fc_loader.get_factory(factory_name)
        self.assertIsNotNone(factory)
        self.assertIsInstance(factory, DrbZarrFactory)

        topic = self.topic_loader.get_drb_topic(self.zarr_id)
        self.assertIsNotNone(factory)
        self.assertEqual(self.zarr_id, topic.id)
        self.assertEqual("zarr", topic.label)
        self.assertIsNone(topic.description)
        self.assertEqual(TopicCategory.FORMATTING, topic.category)
        self.assertEqual(factory_name, topic.factory)

    def test_impl_signatures(self):
        topic = self.topic_loader.get_drb_topic(self.zarr_id)

        node = DrbLogicalNode(self.zarr_ok2)
        self.assertTrue(topic.matches(node))

        node = DrbLogicalNode(self.not_zarr_files)
        self.assertFalse(topic.matches(node))
