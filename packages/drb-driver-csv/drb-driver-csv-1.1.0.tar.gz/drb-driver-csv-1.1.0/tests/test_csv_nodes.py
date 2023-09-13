import pandas
from drb.drivers.file import DrbFileNode
from drb.drivers.csv import CsvBaseNode, CsvRowNode, CsvValueNode
from drb.exceptions.core import DrbException, DrbNotImplementationException
import os
import unittest


class TestCvsBaseNode(unittest.TestCase):
    path = None
    file_node = None
    csv_node = None

    @classmethod
    def setUpClass(cls) -> None:
        resource_dir = os.path.join(os.path.dirname(__file__), 'resources')
        cls.path = os.path.join(resource_dir, 'data.csv')
        cls.file_node = DrbFileNode(cls.path)
        cls.csv_node = CsvBaseNode(cls.file_node)

    def test_csv_base_node(self):
        self.assertEqual(self.file_node.name, self.csv_node.name)
        self.assertEqual(self.file_node.path, self.csv_node.path)
        self.assertEqual(100, len(self.csv_node))

    def test_getitem_by_index(self):
        child = self.csv_node[0]
        self.assertIsNotNone(child)
        self.assertEqual(CsvRowNode, type(child))
        self.assertEqual('row_0', child.name)

        child = self.csv_node[-1]
        self.assertIsNotNone(child)
        self.assertEqual(CsvRowNode, type(child))
        self.assertEqual('row_99', child.name)

        with self.assertRaises(IndexError):
            child = self.csv_node[1024]

        nodes = self.csv_node[3:5]
        self.assertEqual(2, len(nodes))
        self.assertEqual('row_3', nodes[0].name)
        self.assertEqual('row_4', nodes[1].name)

    def test_getitem_by_name(self):
        row_number = 35
        child = self.csv_node[f'row_{row_number}']
        self.assertEqual(self.csv_node[row_number], child)

        with self.assertRaises(KeyError):
            child = self.csv_node['foobar']
        with self.assertRaises(KeyError):
            child = self.csv_node['row_foobar']

    def test_getitem_by_tuple(self):
        child = self.csv_node[('row_1', None, 0)]
        self.assertEqual(self.csv_node[1], child)

        child = self.csv_node[('row_47', 0)]
        self.assertEqual(self.csv_node[47], child)

        child = self.csv_node[('row_31', None)]
        self.assertEqual(self.csv_node[31], child)

        with self.assertRaises(KeyError):
            child = self.csv_node[('row_47', 1)]

    def test_implementation(self):
        supported = self.file_node.impl_capabilities()
        supported.append((pandas.DataFrame, None))
        supported.append((str, None))
        self.assertEqual(set(supported),
                         set(self.csv_node.impl_capabilities()))


class TestCsvRawNode(unittest.TestCase):
    header = ['h1', 'h2', 'h3', 'h4']
    data = ['title', 'section', 'subsection', 'sub-subsection']
    node = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.node = CsvRowNode(None, 'row_3', cls.header, cls.data)

    def test_getitem_int(self):
        node = self.node[-1]
        self.assertIsNotNone(node)
        self.assertEqual('h4', node.name)
        self.assertEqual('sub-subsection', node.value)

        with self.assertRaises(DrbException):
            node[42]

    def test_getitem_name(self):
        node = self.node['h2']
        self.assertIsNotNone(node)
        self.assertEqual('h2', node.name)
        self.assertEqual('section', node.value)

        with self.assertRaises(DrbException):
            node['foobar']

    def test_getitem_tuple(self):
        node = self.node[('h1', None, 0)]
        self.assertIsNotNone(node)
        self.assertEqual('h1', node.name)
        self.assertEqual('title', node.value)

        with self.assertRaises(DrbException):
            node[('h1', 'namespace')]

        with self.assertRaises(DrbException):
            node[('h1', 5)]

    def test_implementation(self):
        self.assertEqual(1, len(self.node.impl_capabilities()))
        with self.assertRaises(DrbNotImplementationException):
            self.node.get_impl(dict)
        self.assertEqual('title, section, subsection, sub-subsection',
                         self.node.get_impl(str))


class TestCsvValueNode(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.node = CsvValueNode(None, 'foobar', 'value')

    def test_attributes(self):
        self.assertEqual({}, self.node.attributes)

    def test_children(self):
        self.assertEqual([], self.node.children)
        self.assertEqual(0, len(self.node))
        self.assertEqual(False, self.node.has_child('foobar'))
        with self.assertRaises(DrbException):
            self.node[0]

    def test_impls(self):
        self.assertEqual(1, len(self.node.impl_capabilities()))
        with self.assertRaises(DrbNotImplementationException):
            self.node.get_impl(int)
        self.assertEqual('value', self.node.get_impl(str))

    def test_value(self):
        node = self.node
        self.assertEqual('value', node.value)
