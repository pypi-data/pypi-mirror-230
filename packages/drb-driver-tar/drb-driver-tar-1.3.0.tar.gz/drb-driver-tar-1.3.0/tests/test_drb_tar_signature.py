import os
import unittest
import uuid
from pathlib import Path

from drb.core.factory import FactoryLoader
from drb.topics.topic import TopicCategory
from drb.topics.dao import ManagerDao
from drb.nodes.logical_node import DrbLogicalNode

from drb.drivers.tar import DrbTarFactory


class TestDrbTarSignature(unittest.TestCase):
    mock_pkg = None
    fc_loader = None
    ic_loader = None

    tar_id = uuid.UUID('60e58ee2-2b5c-11ec-8d3d-0242ac130003')
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))
    tar_test = current_path / "files" / "test.tar"
    empty_file = current_path / "files" / "empty.file"

    @classmethod
    def setUpClass(cls) -> None:
        cls.fc_loader = FactoryLoader()
        cls.ic_loader = ManagerDao()

    def test_impl_loading(self):
        factory_name = 'tar'

        factory = self.fc_loader.get_factory(factory_name)
        self.assertIsNotNone(factory)
        self.assertIsInstance(factory, DrbTarFactory)

        item_class = self.ic_loader.get_drb_topic(self.tar_id)
        self.assertIsNotNone(factory)
        self.assertEqual(self.tar_id, item_class.id)
        self.assertEqual('tar', item_class.label)
        self.assertIsNone(item_class.description)
        self.assertEqual(TopicCategory.CONTAINER, item_class.category)
        self.assertEqual('tar', item_class.factory)

    def test_impl_signatures(self):
        item_class = self.ic_loader.get_drb_topic(self.tar_id)

        node = DrbLogicalNode(self.tar_test)
        self.assertTrue(item_class.matches(node))

        node = DrbLogicalNode(self.empty_file)
        self.assertFalse(item_class.matches(node))
