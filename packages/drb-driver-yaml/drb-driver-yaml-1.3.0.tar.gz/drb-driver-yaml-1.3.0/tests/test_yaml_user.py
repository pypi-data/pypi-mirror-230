import unittest

from drb.drivers.yaml.yaml import YamlNode


class TestYamlUser(unittest.TestCase):
    geo_path = 'tests/resources/geo.yml'

    def test_navigate(self):
        node = YamlNode(self.geo_path)
        self.assertEqual('FeatureCollection', node['type'].value)
        self.assertEqual('Point', node['features'][
            'geometry']['type'].value)
        self.assertEqual([102.0, 0.0], node['features', 1]['geometry'][
            'coordinates'].value)
        self.assertEqual([105.0, 1.0], node['features', 1]['geometry'][
            'coordinates', 3].value)
