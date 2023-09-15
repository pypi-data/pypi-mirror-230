import enum
from typing import List

from deprecated.classic import deprecated
from drb.core.node import DrbNode
from drb.nodes.abstract_node import AbstractNode


class DrbImageNodesValueNames(enum.Enum):
    """
    This enum  represent all metadata as heigth width ...
    """
    IMAGE = 'image'
    TAGS = 'tags'
    FORMAT = 'FormatName'
    WIDTH = 'width'
    HEIGHT = 'height'
    NUM_BANDS = 'NumBands'
    TYPE = 'Type'
    BOUNDARIES = 'Boundaries'
    CRS = 'crs'
    META = 'meta'


class DrbImageSimpleValueNode(AbstractNode):
    """
    This node is used to get simple value such as metadata
    an access the image data,
    usually the first child of the node.

    Parameters:
        parent (DrbNode): The node.
        name (str): the name of the data (usually
                    a value of DrbImageNodesValueNames)
        value (any): the value corresponding to the name.
    """

    def __init__(self, parent: DrbNode, name: str, value: any):
        super().__init__()
        self.name = name
        self.value = value
        self.parent: DrbNode = parent

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError

    @property
    @deprecated(version='1.2.0',
                reason='Usage of the bracket is recommended')
    def children(self) -> List[DrbNode]:
        """
        Not use in this class.

        Returns:
            List: an empty dict ([])
        """
        return []
