from drb.core.factory import FactoryLoader
from drb.exceptions.core import DrbFactoryException
from drb.drivers.file import DrbFileNode
from drb.drivers.csv import CsvBaseNode, CsvNodeFactory
import unittest
import os


class TestCsvFactory(unittest.TestCase):
    resource_dir = os.path.join(os.path.dirname(__file__), 'resources')

    def test_load_factory(self):
        factory_loader = FactoryLoader()
        actual_factory = factory_loader.get_factory('csv')
        self.assertEqual(CsvNodeFactory, type(actual_factory))

    def test_factory(self):
        path = os.path.join(self.resource_dir, 'nuts_area_2021.csv')
        factory = CsvNodeFactory()

        node = factory.create(path)
        self.assertIsNotNone(node)
        self.assertEqual(CsvBaseNode, type(node))

        base_node = DrbFileNode(path)
        node = factory.create(base_node)
        self.assertIsNotNone(node)
        self.assertEqual(CsvBaseNode, type(node))

        with self.assertRaises(DrbFactoryException):
            path = os.path.join(self.resource_dir, 'regular_text.txt')
            factory.create(path)
