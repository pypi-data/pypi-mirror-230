import os
import unittest
import uuid

from drb.core.factory import FactoryLoader
from drb.nodes.logical_node import DrbLogicalNode
from drb.topics.dao import ManagerDao
from drb.topics.topic import TopicCategory

from drb.drivers.yaml import YamlNodeFactory


class TestYamlSignature(unittest.TestCase):
    path = None
    fc_loader = None
    topic_loader = None
    yaml_id = uuid.UUID('3f264232-7c56-11ed-a1eb-0242ac120002')

    @classmethod
    def setUpClass(cls) -> None:
        cls.path = os.path.join(os.path.dirname(__file__),
                                'resources/test.yaml')
        cls.fc_loader = FactoryLoader()
        cls.topic_loader = ManagerDao()

    def test_impl_loading(self):
        factory_name = 'yaml'

        factory = self.fc_loader.get_factory(factory_name)
        self.assertIsNotNone(factory)
        self.assertIsInstance(factory, YamlNodeFactory)

        topic = self.topic_loader.get_drb_topic(self.yaml_id)
        self.assertEqual(self.yaml_id, topic.id)
        self.assertEqual('yaml', topic.label)
        self.assertIsNone(topic.description)
        self.assertEqual(TopicCategory.FORMATTING, topic.category)
        self.assertEqual(factory_name, topic.factory)

    def test_impl_signatures(self):
        topic = self.topic_loader.get_drb_topic(self.yaml_id)

        node = DrbLogicalNode(self.path)
        self.assertTrue(topic.matches(node))
