from io import BufferedIOBase

from drb.core import DrbNode

from drb.drivers.json import JsonNode
from drb.exceptions.core import DrbNotImplementationException, DrbException
import json
import unittest


class TestDrbJson(unittest.TestCase):
    test_path = 'tests/resources/test.json'
    node = JsonNode(test_path)
    with open(test_path) as jsonFile:
        test_data = json.load(jsonFile)

    def test_name(self):
        self.assertEqual('test.json', self.node.name)
        self.assertEqual('species', self.node.children[0].name)
        self.assertEqual('eyeColor', self.node.children[3].children[0].name)

    def test_value(self):
        self.assertEqual(self.test_data, self.node.value)
        self.assertEqual('"Dog"', self.node.children[0].get_impl(str))
        self.assertEqual(6, self.node.children[2].value)
        self.assertIsNotNone(self.node.children[3].value)
        self.assertEqual('"brown"',
                         self.node.children[3].children[0].get_impl(str))
        with self.assertRaises(DrbException):
            self.node.children[3].get_impl(DrbNode)

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
        self.assertEqual(4, len(self.node.children))
        self.assertEqual(3, len(self.node.children[3].children))
        self.assertEqual(2, len(self.node.children[3].children[2].children))
        self.assertEqual(0, len(self.node.children[0].children))
        self.assertEqual(0, len(self.node.children[3].children[0].children))

    def test_bracket(self):
        self.assertEqual('traits', self.node[3].name)
        self.assertEqual('tests/resources/test.json/traits',
                         self.node['traits'].path.path)
        with self.assertRaises(KeyError):
            self.node['toto']
        with self.assertRaises(NotImplementedError):
            del self.node['traits']
        with self.assertRaises(NotImplementedError):
            self.node[None] = JsonNode(path={'titi': 'bird'})

    def test_get_attributes(self):
        with self.assertRaises(DrbException):
            self.node.get_attribute('something')
        with self.assertRaises(DrbException):
            self.node @ 'something'
        with self.assertRaises(DrbException):
            self.node.children[3].get_attribute('something')
        with self.assertRaises(DrbException):
            self.node.children[3].children[0].get_attribute(
                'something'
            )
        self.node @= ('something', 'tata')
        self.assertEqual('tata', self.node @ 'something')
        self.assertEqual({('something', None)},
                         self.node.attribute_names())
        self.node @= ('name', 'namespace', 'toto')
        self.assertEqual('toto', self.node @ ('name', 'namespace'))
        self.assertEqual(
            {('something', None), ('name', 'namespace')},
            self.node.attribute_names())

    def test_has_child(self):
        self.assertTrue(self.node.has_child())
        self.assertTrue(self.node.has_child('species'))
        self.assertFalse(self.node.has_child('nothing'))
        self.assertFalse(self.node.has_child('species', 'ns'))
        self.assertTrue(self.node.children[3].has_child())
        self.assertTrue(self.node.children[3].children[2].has_child())
        self.assertFalse(self.node.children[0].has_child())
        self.assertFalse(self.node.children[3].children[0].has_child())

    def test_has_impl(self):
        self.assertTrue(self.node.has_impl(str))
        self.assertTrue(self.node.children[0].has_impl(str))
        self.assertFalse(self.node.children[3].children[0].has_impl(int))
        self.assertFalse(self.node.children[3].has_impl(bool))

    def test_capabilities(self):
        self.assertEqual(4, len(self.node.impl_capabilities()))
        expected = [BufferedIOBase, dict, str, list]
        self.assertEqual(set([(x, None) for x in expected]),
                         set(self.node.impl_capabilities()))

    def test_get_impl(self):
        self.assertEqual('"Dog"', self.node.children[0].get_impl(str))
        self.assertEqual(b'"Dog"',
                         self.node['species'].get_impl(BufferedIOBase).read())
        with self.assertRaises(DrbNotImplementationException):
            self.node.get_impl(DrbNode)

    def test_close(self):
        self.node.close()

    def test_path(self):
        self.assertEqual('tests/resources/test.json', self.node.path.path)
        self.assertEqual('tests/resources/test.json/species',
                         self.node.children[0].path.path)
        self.assertEqual('tests/resources/test.json/traits/eyeColor',
                         self.node.children[3].children[0].path.path)

    def test_geo(self):
        self.assertEqual('tests/resources/test.json',
                         self.node.path.path)
        self.assertEqual('tests/resources/test.json/species',
                         self.node.children[0].path.path)
        self.assertEqual('tests/resources/test.json/traits/eyeColor',
                         self.node.children[3].children[0].path.path)
