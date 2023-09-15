from typing import List

from deprecated.classic import deprecated
from drb.core.node import DrbNode
from drb.nodes.abstract_node import AbstractNode
from drb.topics.resolver import resolve_children


class DrbImageListNode(AbstractNode):
    """
    This node is used to have one or many children of DrbNode but no value.
    Usually it will be a list of DrbImageSimpleValueNode.

    Parameters:
        parent (DrbNode): The node parent.
        name (str): the name of the data (usually a
                    value of DrbImageNodesValueNames)
    """
    def __init__(self, parent: DrbNode, name: str):
        super().__init__()

        self.name = name
        self.parent: DrbNode = parent
        self._children: List[DrbNode] = []

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError

    @property
    @deprecated(version='1.2.0',
                reason='Usage of the bracket is recommended')
    @resolve_children
    def children(self) -> List[DrbNode]:
        """
        Return a list of DrbNode representing the children of this node.

        Returns:
            List[DrbNode]: The children of this node.
        """
        return self._children

    def append_child(self, node: DrbNode) -> None:
        """
        Appends a DrbNode giving in argument to the list of children.

        Parameters:
            node (DrbNode): The node to add.
        """
        self._children.append(node)
