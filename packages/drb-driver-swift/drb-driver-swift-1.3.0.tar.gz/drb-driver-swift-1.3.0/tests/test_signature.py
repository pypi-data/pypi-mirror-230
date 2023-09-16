import unittest
import uuid

from drb.core.factory import FactoryLoader
from drb.topics.topic import TopicCategory
from drb.topics.dao import ManagerDao
from drb.nodes.logical_node import DrbLogicalNode

from drb.drivers.swift import SwiftNodeFactory


class TestSwiftSignature(unittest.TestCase):
    swift_id = uuid.UUID('86289118-7797-11ec-90d6-0242ac120003')
    storage_url = "https+swift://my.swift/"
    storage_url2 = "http+swift://my.swift/"
    storage_url3 = "https://my.swift/"
    fc_loader = None
    ic_loader = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.fc_loader = FactoryLoader()
        cls.ic_loader = ManagerDao()

    def test_impl_loading(self):
        factory_name = 'swift'

        factory = self.fc_loader.get_factory(factory_name)
        self.assertIsNotNone(factory)
        self.assertIsInstance(factory, SwiftNodeFactory)

        topic = self.ic_loader.get_drb_topic(self.swift_id)
        self.assertIsNotNone(factory)
        self.assertEqual(self.swift_id, topic.id)
        self.assertEqual('swift', topic.label)
        self.assertIsNone(topic.description)
        self.assertEqual(TopicCategory.CONTAINER, topic.category)
        self.assertEqual('swift', topic.factory)

    def test_impl_signatures(self):
        item_class = self.ic_loader.get_drb_topic(self.swift_id)

        node = DrbLogicalNode(self.storage_url)
        self.assertTrue(item_class.matches(node))

        node = DrbLogicalNode(self.storage_url2)
        self.assertTrue(item_class.matches(node))

        node = DrbLogicalNode(self.storage_url3)
        self.assertFalse(item_class.matches(node))
