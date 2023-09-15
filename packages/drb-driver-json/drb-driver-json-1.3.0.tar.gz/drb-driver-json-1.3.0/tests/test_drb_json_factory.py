from drb.exceptions.core import DrbException
from drb.drivers.file import DrbFileNode
from drb.drivers.json import JsonNodeFactory, JsonBaseNode, JsonNode
import unittest


class TestJsonFactoryNode(unittest.TestCase):
    path = 'tests/resources/test.json'
    invalid_path = 'tests/resources/not_here.json'
    file = DrbFileNode(path)

    def test_create_from_file(self):
        node = JsonNodeFactory()._create(self.path)

        self.assertIsNotNone(node)
        self.assertIsInstance(node, JsonNode)
        self.assertEqual("test.json", node.name)
        node.close()

    def test_from_node(self):
        factory = JsonNodeFactory()
        node_file = DrbFileNode(self.path)

        node = factory.create(node_file)
        self.assertIsNotNone(node)
        self.assertIsInstance(node, JsonBaseNode)
        node.close()

    def test_fails(self):
        factory = JsonNodeFactory()
        with self.assertRaises(DrbException):
            factory.create(self.invalid_path)
