import abc
from typing import List, Any

from deprecated.classic import deprecated
from drb.core import DrbNode
from drb.exceptions.core import DrbNotImplementationException
from drb.nodes.abstract_node import AbstractNode

NAMESPACE_GRIB_NODE = None


class DrbGribAbstractNode(AbstractNode, abc.ABC):

    def __init__(self, parent: DrbNode, name: str):
        super().__init__()
        self.parent: DrbNode = parent
        self.name = name
        self.namespace_uri = NAMESPACE_GRIB_NODE

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError


class DrbGribSimpleValueNode(DrbGribAbstractNode):
    """
    This node is used to get a simple value.

    Parameters:
        parent (DrbNode): The parent of the node.
        name (str): the name of the node.
        value (any): the value.
    """
    def __init__(self, parent: DrbNode, name: str, value: any):
        super().__init__(parent, name)
        self.value = value

    @property
    @deprecated(version='1.2.0',
                reason='Usage of the bracket is recommended')
    def children(self) -> List[DrbNode]:
        """
        This node as no children.

        Returns:
            List: An empty List
        """
        return []
