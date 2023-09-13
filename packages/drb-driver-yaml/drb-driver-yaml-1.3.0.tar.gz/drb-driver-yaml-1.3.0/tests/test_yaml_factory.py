import unittest

from drb.drivers.file import DrbFileNode
from drb.exceptions.core import DrbException

from drb.drivers.yaml import YamlNodeFactory, YamlNode, YamlBaseNode


class TestYamlFactoryNode(unittest.TestCase):
    path = 'tests/resources/test.yml'
    invalid_path = 'tests/resources/not_here.yml'
    file = DrbFileNode(path)

    def test_create_from_file(self):
        node = YamlNodeFactory()._create(self.path)

        self.assertIsNotNone(node)
        self.assertIsInstance(node, YamlNode)
        self.assertEqual("test.yml", node.name)
        node.close()

    def test_create_from_yaml(self):
        tmp = YamlNode(self.path)
        node = YamlNodeFactory()._create(self.path)

        self.assertIsNotNone(node)
        self.assertIsInstance(node, YamlNode)
        self.assertEqual(node, tmp)
        self.assertEqual("test.yml", node.name)

    def test_from_node(self):
        factory = YamlNodeFactory()
        node_file = DrbFileNode(self.path)

        node = factory.create(node_file)
        self.assertIsNotNone(node)
        self.assertIsInstance(node, YamlBaseNode)
        node.close()

    def test_fails(self):
        factory = YamlNodeFactory()
        with self.assertRaises(DrbException):
            factory.create(self.invalid_path)
