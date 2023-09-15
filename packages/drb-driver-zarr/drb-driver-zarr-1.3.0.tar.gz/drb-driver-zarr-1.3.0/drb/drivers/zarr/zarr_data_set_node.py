import enum
from abc import ABC
from typing import Any, List, Union, Dict, Tuple

import drb.topics.resolver as resolver
import zarr
from deprecated.classic import deprecated

from drb.core import DrbNode
from drb.nodes.abstract_node import AbstractNode
from drb.exceptions.core import DrbNotImplementationException, DrbException


class DrbZarrAttributeNames(enum.Enum):
    """
    A Boolean that tell if the zarr is read only.
    """

    READ_ONLY = "read_only"


class DrbZarrDataSetNode(AbstractNode, ABC):
    """
    This node will be inherited by DrbZarrGroupNode and DrbZarrArrayNode.

    Parameters:
        parent (DrbNode): The parent of the node.
        name (str): The name of the node.
        data_set (Union[zarr.hierarchy.Group, zarr.core.Array]):
                 the dataset of the node
                 corresponding to a zarr group
                 otherwise a zarr array.
    """

    def __init__(
        self,
        parent: DrbNode,
        name: str,
        data_set: Union[zarr.hierarchy.Group, zarr.core.Array],
    ):
        super().__init__()

        self._data_set = data_set
        self.parent: DrbNode = parent
        self.name = name
        self.add_impl(data_set.__class__, _to_dataset)
        self._attributes: Dict[Tuple[str, str], Any] = None
        self.__init_attributes()

    def __init_attributes(self):
        for key in self._data_set.attrs.keys():
            self @= (key, self._data_set.attrs[key])
        self @= (DrbZarrAttributeNames.READ_ONLY.value,
                 self._data_set.read_only)

    @staticmethod
    def create_node_from_data_set(parent, data_set):
        name = data_set.name
        if name and name[0] == "/":
            name = name[1:]
        if not name:
            name = "."
        if isinstance(data_set, zarr.hierarchy.Group):
            node = DrbZarrGroupNode(parent, name, data_set)
        else:
            node = DrbZarrArrayNode(parent, name, data_set)
        return node

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError


class DrbZarrGroupNode(DrbZarrDataSetNode):
    """
    This node is used to organize the data in a zarr architecture,
    he contains a group of zarr array in his children
    or another DrbZarrGroupNode.

    Parameters:
        parent (DrbNode): The parent of the node.
        name (str): The name of the node.
        data_set (Union[zarr.hierarchy.Group, zarr.core.Array]):
                 the dataset of the node
                 corresponding to a zarr group
                 otherwise a zarr array.
    """

    def __init__(
        self,
        parent: DrbNode,
        name: str,
        data_set: Union[zarr.hierarchy.Group, zarr.core.Array],
    ):
        super().__init__(parent, name, data_set)
        self._children: List[DrbNode] = None

    @property
    @deprecated(version="1.2.0", reason="drb core deprecation since 2.1.0")
    @resolver.resolve_children
    def children(self) -> List[DrbNode]:
        if self._children is None:
            self._children = []
            self._data_set.visitvalues(self.add_data_set_children)
        return self._children

    def add_data_set_children(self, data_set):
        """
        Add the dataset given in argument to the List of children.

        Parameters:
            data_set : a data set to be added in the children List.
        """
        child = DrbZarrDataSetNode.create_node_from_data_set(self, data_set)
        self._children.append(child)

    def _get_named_child(
        self,
        name: str,
        namespace_uri: str = None,
        occurrence: Union[int, slice] = 0,
    ) -> Union[DrbNode, List[DrbNode]]:
        if self._children is None:
            if namespace_uri is None:
                data_set = self._data_set[name]
                return [self.create_node_from_data_set(self, data_set)][
                    occurrence
                ]

            raise DrbException(
                f"No child found having name: {name} and"
                f" namespace: {namespace_uri}"
            )
        else:
            return super()._get_named_child(name, namespace_uri, occurrence)


class DrbZarrArrayNode(DrbZarrDataSetNode):
    """
    This node is used to represent one or a set of values
    contained in a Zarr array.

    Parameters:
        parent (DrbNode): The parent of the node.
        name (str): The name of the node.
        data_set (Union[zarr.hierarchy.Group, zarr.core.Array]):
                 the dataset of the node
                 corresponding to a zarr group
                 otherwise a zarr array.
    """

    def __init__(
        self,
        parent: DrbNode,
        name: str,
        data_set: Union[zarr.hierarchy.Group, zarr.core.Array],
    ):
        super().__init__(parent, name, data_set)

    @property
    @deprecated(version="1.2.0", reason="drb core deprecation since 2.1.0")
    def children(self) -> List[DrbNode]:
        return []


def _to_dataset(node: DrbZarrDataSetNode, **kwargs):
    return node._data_set
