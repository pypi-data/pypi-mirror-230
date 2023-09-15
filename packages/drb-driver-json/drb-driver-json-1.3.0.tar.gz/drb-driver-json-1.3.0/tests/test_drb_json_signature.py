from drb.core.factory import FactoryLoader
from drb.nodes.logical_node import DrbLogicalNode
from drb.topics.dao import ManagerDao

from drb.topics.topic import TopicCategory

from drb.drivers.json import JsonNodeFactory
import os
import unittest
import uuid


class TestJsonSignature(unittest.TestCase):
    path = None
    fc_loader = None
    ic_loader = None
    json_id = uuid.UUID('c6f7d210-4df0-11ec-81d3-0242ac130003')

    @classmethod
    def setUpClass(cls) -> None:
        cls.path = os.path.join(os.path.dirname(__file__),
                                'resources/test.json')
        cls.fc_loader = FactoryLoader()
        cls.topic_loader = ManagerDao()

    def test_impl_loading(self):
        factory_name = 'json'

        factory = self.fc_loader.get_factory(factory_name)
        self.assertIsNotNone(factory)
        self.assertIsInstance(factory, JsonNodeFactory)

        topic = self.topic_loader.get_drb_topic(self.json_id)
        self.assertIsNotNone(factory)
        self.assertEqual(self.json_id, topic.id)
        self.assertEqual('json', topic.label)
        self.assertIsNone(topic.description)
        self.assertEqual(TopicCategory.FORMATTING, topic.category)
        self.assertEqual(factory_name, topic.factory)

    def test_impl_signatures(self):
        topic = self.topic_loader.get_drb_topic(self.json_id)

        node = DrbLogicalNode(self.path)
        self.assertTrue(topic.matches(node))

        node = DrbLogicalNode('https://gitlab.com/drb-python')
        self.assertFalse(topic.matches(node))
