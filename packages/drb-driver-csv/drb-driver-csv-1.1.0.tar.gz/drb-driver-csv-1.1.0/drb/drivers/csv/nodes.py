from deprecated import deprecated
from typing import Any, List, Dict, Tuple
from drb.core import DrbNode, ParsedPath
from drb.nodes.abstract_node import AbstractNode
from drb.nodes.logical_node import WrappedNode
from drb.exceptions.core import DrbException
import io
import csv
import pandas
import copy


def _base_node_to_panda_dataframe(node: DrbNode, **kwargs):
    return pandas.read_csv(node.get_impl(io.BufferedIOBase))


def _base_node_to_str(node: DrbNode, **kwargs):
    return _base_node_to_panda_dataframe(node).to_string()


class CsvBaseNode(WrappedNode):
    def __init__(self, base_node: DrbNode, **kwargs):
        super().__init__(base_node)
        with self._wrapped.get_impl(io.BufferedIOBase) as stream:
            # try to retrieve dialect reading the first 1024 strings
            self._dialect = csv.Sniffer().sniff(stream.read(1024).decode())
        with self._wrapped.get_impl(io.BufferedIOBase) as stream:
            charset = kwargs.get('charset', 'utf-8')
            with io.TextIOWrapper(stream, encoding=charset) as data:
                reader = csv.reader(data, dialect=self._dialect)
                self._header = next(reader)
                self._children = [
                    CsvRowNode(self, f'row_{i}', self._header, v)
                    for i, v in enumerate(reader)
                ]
        self._impl_mng = copy.copy(self._wrapped._impl_mng)
        self.add_impl(pandas.DataFrame, _base_node_to_panda_dataframe)
        self.add_impl(str, _base_node_to_str)

    def __len__(self):
        return len(self._children)

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, item):
        raise NotImplementedError

    @staticmethod
    def __extract_index_from_name(name: str) -> int:
        return int(name.split('row_')[1])

    @property
    def path(self) -> ParsedPath:
        return self._wrapped.path

    @property
    @deprecated(
        version='2.1.0',
        reason='Please use bracket to access to node child(ren)'
    )
    def children(self) -> List[DrbNode]:
        return self._children


class CsvRowNode(AbstractNode):
    def __init__(self, parent: DrbNode, name: str, header: List[str],
                 data: List[str]):
        super().__init__()
        self.parent = parent
        self.name = name
        self._header = header
        self._data = data
        self.add_impl(str, self.__impl_str)

    def __repr__(self):
        return f"CsvRowNode({str(self._data)})"

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, item):
        raise NotImplementedError

    @property
    def children(self) -> List[DrbNode]:
        return [
            CsvValueNode(self, name, self._data[idx])
            for idx, name in enumerate(self._header)
        ]

    @staticmethod
    def __impl_str(node: DrbNode, **kwargs):
        return ', '.join(map(str, node._data))


class CsvValueNode(DrbNode):
    def __init__(self, parent: DrbNode, name: str, value: str):
        super().__init__()
        self.name = name
        self.parent = parent
        self.value = value
        self.add_impl(str, str)

    @property
    @deprecated(version='2.1.0')
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        return {(n, ns): self @ (n, ns) for n, ns in self.attribute_names()}

    @property
    @deprecated(version='2.1.0')
    def children(self) -> List[DrbNode]:
        return []

    def __len__(self):
        return 0

    def __getitem__(self, item):
        raise DrbException(f'child not {item} found')

    def __repr__(self):
        return self.value

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, item):
        raise NotImplementedError

    def has_child(self, name: str = None, namespace: str = None) -> bool:
        return False
