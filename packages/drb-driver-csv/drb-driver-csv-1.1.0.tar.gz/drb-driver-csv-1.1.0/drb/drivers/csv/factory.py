from drb.core import DrbNode, DrbFactory
from drb.exceptions.core import DrbFactoryException
from .nodes import CsvBaseNode


class CsvNodeFactory(DrbFactory):
    def _create(self, node: DrbNode) -> DrbNode:
        if isinstance(node, CsvBaseNode):
            return node
        try:
            return CsvBaseNode(node)
        except Exception as ex:
            raise DrbFactoryException from ex
