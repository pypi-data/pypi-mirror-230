import unittest

from drb.drivers.json import JsonNode


class TestDrbJsonUser(unittest.TestCase):
    geo_path = 'tests/resources/geo.json'

    def test_navigate(self):
        node = JsonNode(self.geo_path)
        self.assertEqual('FeatureCollection', node['type'].value)
        self.assertEqual('Point', node['features'][
            'geometry']['type'].value)
        self.assertEqual([102.0, 0.0], node['features', 1]['geometry'][
            'coordinates'].value)
        self.assertEqual([105.0, 1.0], node['features', 1]['geometry'][
            'coordinates', 3].value)
