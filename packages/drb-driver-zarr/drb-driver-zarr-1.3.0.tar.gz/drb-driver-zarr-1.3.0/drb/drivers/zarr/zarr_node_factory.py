from typing import Any, List, Dict, Tuple, Optional

from deprecated.classic import deprecated
from drb.core import DrbNode
from drb.nodes.abstract_node import AbstractNode
from drb.core.factory import DrbFactory
from drb.core.path import ParsedPath
import zarr
import copy

from drb.exceptions.zarr import DrbZarrNodeException
from .zarr_data_set_node import DrbZarrDataSetNode


class DrbZarrNode(AbstractNode):
    """
    This node is used to instantiate a DrbZarrNode
    from another implementation of drb such as file.

    Parameters:
        base_node (DrbNode): the base node of this node.
    """

    def __init__(self, base_node: DrbNode):
        super().__init__()

        self.base_node = base_node
        self._impl_mng = copy.copy(self.base_node._impl_mng)
        self._children: List[DrbNode] = None

    @property
    def parent(self) -> Optional[DrbNode]:
        return self.base_node.parent

    @property
    def path(self) -> ParsedPath:
        return self.base_node.path

    @property
    def name(self) -> str:
        return self.base_node.name

    @property
    def namespace_uri(self) -> Optional[str]:
        return self.base_node.namespace_uri

    @property
    def value(self) -> Optional[Any]:
        return self.base_node.value

    @property
    @deprecated(version="1.2.0", reason="drb core deprecation since 2.1.0")
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        return self.base_node.attributes

    @deprecated(version="1.2.0", reason="drb core deprecation since 2.1.0")
    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        return self.base_node.get_attribute(name, namespace_uri)

    @property
    @deprecated(version="1.2.0", reason="drb core deprecation since 2.1.0")
    def children(self) -> List[DrbNode]:
        if self._children is None:
            try:
                root_data_set = zarr.open(self.base_node.path.name)
                root_node = DrbZarrDataSetNode.create_node_from_data_set(
                    self, root_data_set
                )
                self._children = [root_node]
            except Exception as e:
                raise DrbZarrNodeException(
                    f"Unable to read zarr file" f" {self.name} "
                ) from e
        return self._children

    def has_child(self, name: str = None, namespace: str = None) -> bool:
        if namespace is not None:
            return False
        return super().has_child(name, namespace)

    def close(self):
        self.base_node.close()

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError


class DrbZarrFactory(DrbFactory):
    def _create(self, node: DrbNode) -> DrbNode:
        if isinstance(node, DrbZarrNode):
            return node
        return DrbZarrNode(base_node=node)
