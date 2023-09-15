import os
import unittest
import uuid
from pathlib import Path

from drb.core.factory import FactoryLoader
from drb.nodes.logical_node import DrbLogicalNode
from drb.topics.dao import ManagerDao
from drb.topics.topic import TopicCategory

from drb.drivers.grib import DrbGribFactory


class TestDrbGribSignature(unittest.TestCase):
    fc_loader = None
    topic_loader = None

    grib_id = uuid.UUID('06facbd4-437e-420c-981d-0414028a6b22')
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))
    grib_file = current_path / "files" / 'temp.grib'
    empty_file = current_path / "files" / "empty.file"

    @classmethod
    def setUpClass(cls) -> None:
        cls.fc_loader = FactoryLoader()
        cls.topic_loader = ManagerDao()

    def test_impl_loading(self):
        factory_name = 'grib'

        factory = self.fc_loader.get_factory(factory_name)
        self.assertIsNotNone(factory)
        self.assertIsInstance(factory, DrbGribFactory)

        topic = self.topic_loader.get_drb_topic(self.grib_id)
        self.assertIsNotNone(factory)
        self.assertEqual(self.grib_id, topic.id)
        self.assertEqual('GRIB', topic.label)
        self.assertIsNone(topic.description)
        self.assertEqual(TopicCategory.FORMATTING, topic.category)
        self.assertEqual(factory_name, topic.factory)

    def test_impl_signatures(self):
        topic = self.topic_loader.get_drb_topic(self.grib_id)

        node = DrbLogicalNode(self.grib_file)
        self.assertTrue(topic.matches(node))

        node = DrbLogicalNode(self.empty_file)
        self.assertFalse(topic.matches(node))
