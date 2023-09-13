import os
import unittest
import uuid
from pathlib import Path

from drb.core.factory import FactoryLoader
from drb.topics.topic import TopicCategory
from drb.topics.dao import ManagerDao
from drb.nodes.logical_node import DrbLogicalNode

from drb.drivers.zip import DrbZipFactory


class TestDrbZipSignature(unittest.TestCase):
    fc_loader = None
    ic_loader = None
    zip_id = uuid.UUID('da61a26a-2b34-11ec-8d3d-0242ac130003')
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))
    zip_ok2 = current_path / "files" / "data-ok2.zip"
    not_zip_files = current_path / "files" / "mydata.txt"
    zip_case = current_path / "files" / "mydata.Zip"

    @classmethod
    def setUpClass(cls) -> None:
        cls.fc_loader = FactoryLoader()
        cls.ic_loader = ManagerDao()

    def test_impl_loading(self):
        factory_name = 'zip'

        factory = self.fc_loader.get_factory(factory_name)
        self.assertIsNotNone(factory)
        self.assertIsInstance(factory, DrbZipFactory)

        item_class = self.ic_loader.get_drb_topic(self.zip_id)
        self.assertIsNotNone(factory)
        self.assertEqual(self.zip_id, item_class.id)
        self.assertEqual('zip', item_class.label)
        self.assertIsNone(item_class.description)
        self.assertEqual(TopicCategory.CONTAINER, item_class.category)
        self.assertEqual(factory_name, item_class.factory)

    def test_impl_signatures(self):
        item_class = self.ic_loader.get_drb_topic(self.zip_id)

        node = DrbLogicalNode(self.zip_ok2)
        self.assertTrue(item_class.matches(node))

        node = DrbLogicalNode(self.zip_case)
        self.assertTrue(item_class.matches(node))

        node = DrbLogicalNode('https://gitlab.com/drb-python')
        self.assertFalse(item_class.matches(node))
