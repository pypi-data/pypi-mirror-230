import io

import yaml
import unittest

from drb.exceptions.core import DrbException, DrbNotImplementationException

from drb.drivers.yaml import YamlNode


class TestDrbYaml(unittest.TestCase):
    test_path = 'tests/resources/test.yml'
    node = YamlNode(test_path)
    with open(test_path) as yamlFile:
        test_data = yaml.safe_load(yamlFile)

    def test_name(self):
        self.assertEqual('test.yml', self.node.name)
        self.assertEqual('species', self.node.children[0].name)
        self.assertEqual('eyeColor', self.node.children[3].children[0].name)

    def test_value(self):
        self.assertEqual(self.test_data, self.node.value)
        self.assertEqual('Dog\n...\n', self.node.children[0].get_impl(str))
        self.assertEqual(6, self.node.children[2].value)
        self.assertIsNotNone(self.node.children[3].value)
        self.assertEqual('brown\n...\n',
                         self.node.children[3].children[0].get_impl(str))
        with self.assertRaises(DrbException):
            self.node.children[3].get_impl(int)

    def test_attributes(self):
        self.assertEqual({}, self.node.attributes)
        self.assertEqual({}, self.node.children[3].attributes)
        self.assertEqual({}, self.node.children[3].children[0].attributes)

    def test_parent(self):
        self.assertIsNone(self.node.parent)
        self.assertEqual(self.node, self.node.children[2].parent)
        self.assertEqual(self.node.children[3],
                         self.node.children[3].children[0].parent
                         )

    def test_children(self):
        self.assertEqual(4, len(self.node))
        self.assertEqual(3, len(self.node[3]))
        self.assertEqual(2, len(self.node[3][2]))
        self.assertEqual(0, len(self.node[0]))
        self.assertEqual(0, len(self.node[3][0]))

    def test_get_attributes(self):
        with self.assertRaises(DrbException):
            self.node.get_attribute('something')
        with self.assertRaises(DrbException):
            self.node @ 'something'
        with self.assertRaises(DrbException):
            self.node.children[3] @ 'something'
        with self.assertRaises(DrbException):
            self.node.children[3] @ 'something'

    def test_has_child(self):
        self.assertTrue(self.node.has_child())
        self.assertTrue(self.node.has_child('species'))
        self.assertFalse(self.node.has_child('nothing'))
        self.assertFalse(self.node.has_child('species', 'ns'))
        self.assertTrue(self.node[3].has_child())
        self.assertTrue(self.node[3][2].has_child())
        self.assertFalse(self.node[0].has_child())
        self.assertFalse(self.node[3][0].has_child())

    def test_has_impl(self):
        self.assertTrue(self.node.has_impl(str))
        self.assertTrue(self.node[0].has_impl(str))
        self.assertFalse(self.node[3][0].has_impl(int))
        self.assertFalse(self.node[3].has_impl(bool))

    def test_get_impl(self):
        self.assertEqual('Dog\n...\n', self.node[0].get_impl(str))
        self.assertIsInstance(self.node[0].get_impl(io.BufferedIOBase),
                              io.BytesIO)
        self.assertEqual(b'Dog\n...\n',
                         self.node[0].get_impl(io.BufferedIOBase).read())
        with self.assertRaises(DrbNotImplementationException):
            self.node.get_impl(int)

    def test_close(self):
        self.node.close()

    def test_path(self):
        self.assertEqual('tests/resources/test.yml', self.node.path.path)
        self.assertEqual('tests/resources/test.yml/species',
                         self.node.children[0].path.path)
        self.assertEqual('tests/resources/test.yml/traits/eyeColor',
                         self.node.children[3].children[0].path.path)

    def test_geo(self):
        self.assertEqual('tests/resources/test.yml',
                         self.node.path.path)
        self.assertEqual('tests/resources/test.yml/species',
                         self.node.children[0].path.path)
        self.assertEqual('tests/resources/test.yml/traits/eyeColor',
                         self.node.children[3].children[0].path.path)
