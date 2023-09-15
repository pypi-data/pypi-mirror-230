from drb.exceptions.core import DrbException
from drb.drivers.file import DrbFileNode
from drb.drivers.json import JsonNode, JsonBaseNode
from typing import Tuple
import io
import unittest


class TestJsonBaseNode(unittest.TestCase):
    path = 'tests/resources/test.json'
    file_node = None
    node = None

    @classmethod
    def create_tmp_node(cls) -> Tuple[JsonBaseNode, DrbFileNode]:
        file_node = DrbFileNode(cls.path)
        with io.FileIO(cls.path) as stream:
            return JsonBaseNode(file_node, stream), file_node

    @classmethod
    def setUpClass(cls) -> None:
        cls.node, cls.file_node = cls.create_tmp_node()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.node.close()

    def test_name(self):
        self.assertEqual(self.file_node.name, self.node.name)

    def test_value(self):
        self.assertFalse(self.node.has_impl(int))
        self.assertTrue(self.node.has_impl(io.BufferedIOBase))
        self.assertTrue(self.node.has_impl(io.FileIO))
        self.assertEqual(self.file_node.value, self.node.value)

    def test_namespace_uri(self):
        self.assertEqual(self.file_node.namespace_uri, self.node.namespace_uri)

    def test_attributes(self):
        self.assertEqual(self.file_node.attributes, self.node.attributes)

    def test_parent(self):
        self.assertEqual(self.file_node.parent, self.node.parent)

    def test_children(self):
        children = self.node.children
        self.assertIsNotNone(children)
        self.assertIsInstance(children, list)
        self.assertEqual(1, len(children))
        self.assertIsInstance(children[0], JsonNode)

    def test_get_attribute(self):
        with self.assertRaises(DrbException):
            self.node.get_attribute('key')

    def test_has_child(self):
        self.assertTrue(self.node.has_child())

    def test_get_children_number(self):
        self.assertEqual(1, len(self.node))

    def test_close(self):
        node, file_node = self.create_tmp_node()
        node.close()
        file_node.close()

    def test_path(self):
        children = self.node.children
        self.assertIsNotNone(children)
        self.assertIsInstance(children, list)
        self.assertEqual(1, len(children))
        self.assertIsInstance(children[0], JsonNode)
        self.assertEqual(children[0].path.path, self.node.path.path)
