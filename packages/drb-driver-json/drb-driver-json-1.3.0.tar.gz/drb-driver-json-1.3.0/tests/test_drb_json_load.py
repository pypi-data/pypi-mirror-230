from drb.drivers.json import JsonNodeFactory
import json
import unittest


class TestDrbJsonLoad(unittest.TestCase):
    array_path = 'tests/resources/array.json'
    with open(array_path) as jsonFile:
        test_data = json.load(jsonFile)
    DICT = {
        "value1": "toot",
        "value2": "2",
        "value3": [3, 2]

    }
    ARRAY = [
        {"value1": 1},
        {"value2": 2},
        {"value3": 3}
    ]

    def test_load_dict_var(self):
        node = JsonNodeFactory()._create(self.DICT)
        self.assertIsNone(node.name)
        self.assertEqual('/', node.path.path)
        self.assertEqual("toot", node.children[0].value)
        self.assertEqual('"2"', node.children[1].get_impl(str))
        self.assertEqual(3, node.children[2].value)

    def test_load_array_var(self):
        node = JsonNodeFactory()._create(self.ARRAY)
        self.assertIsNone(node.name)
        self.assertEqual('/', node.path.path)
        self.assertEqual('', node.children[0].name)
        self.assertEqual({'value1': 1}, node.children[0].value)
        self.assertEqual('/value1', node.children[0].children[0].path.path)
        self.assertEqual(1, node.children[0].children[0].value)

    def test_load_array_file(self):
        node = JsonNodeFactory()._create(self.array_path)
        self.assertEqual('array.json', node.name)
        self.assertEqual(self.test_data, node.value)
        self.assertEqual(2, node.children[1].value)
        self.assertEqual(1, node.children[0].children[0].value)
        self.assertEqual('value1', node.children[0].children[0].name)
        self.assertEqual('"value3"',
                         node.children[2].children[0].get_impl(str))
