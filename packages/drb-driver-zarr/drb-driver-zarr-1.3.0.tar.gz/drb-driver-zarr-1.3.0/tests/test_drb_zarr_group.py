import io
import os
import unittest
from pathlib import Path

import zarr.hierarchy
from drb.exceptions.core import DrbNotImplementationException, DrbException
from drb.drivers.file import DrbFileFactory

from drb.drivers.zarr import DrbZarrFactory
from drb.drivers.zarr.zarr_data_set_node import (
    DrbZarrGroupNode,
    DrbZarrArrayNode,
    DrbZarrAttributeNames,
)


class TestDrbGroupNodeZarr(unittest.TestCase):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))

    zarr_group = current_path / "files" / "group.zarr"

    zarr_ok2 = current_path / "files" / "sample.zarr"
    zarr_without_group = current_path / "files" / "example.zarr"

    def setUp(self) -> None:
        self.node = None
        self.node_file = None

    def tearDown(self) -> None:
        if self.node is not None:
            self.node.close()
        if self.node_file is not None:
            self.node_file.close()

    def open_node(self, path_file):
        self.node_file = DrbFileFactory().create(path_file)
        self.node = DrbZarrFactory().create(self.node_file)
        return self.node

    def test_first_group(self):
        node = self.open_node(str(self.zarr_ok2))

        root_node = node[0]

        self.assertIsInstance(root_node, DrbZarrGroupNode)
        self.assertEqual(root_node.name, ".")
        self.assertEqual(root_node.namespace_uri, None)

    def test_children_group(self):
        node = self.open_node(str(self.zarr_ok2))

        root_node = node[0]

        self.assertIsInstance(root_node, DrbZarrGroupNode)
        self.assertTrue(root_node.has_child())
        self.assertTrue(root_node.has_child("traffic_light_faces"))
        self.assertFalse(root_node.has_child("traffic_light_face"))
        self.assertTrue(root_node.has_child("traffic_light_faces", None))
        self.assertFalse(root_node.has_child("traffic_light_faces", "ns"))
        self.assertFalse(root_node.has_child("traffic_light_face", None))

        self.assertEqual(len(root_node), 4)

    def test_list_child(self):
        node = self.open_node(str(self.zarr_ok2))

        root_node = node[0]

        list_child_named = root_node["traffic_light_faces", None, :]
        self.assertIsNotNone(list_child_named)

    def test_get_child_group(self):
        node = self.open_node(str(self.zarr_ok2))

        root_node = node[0]

        self.assertIsNotNone(root_node[("traffic_light_faces", 0)])

        self.assertIsNotNone(root_node["traffic_light_faces"])

        child_t_l_faces = root_node["traffic_light_faces"]
        self.assertEqual(child_t_l_faces.name, "traffic_light_faces")

        with self.assertRaises(KeyError):
            root_node[("traffic_light_faces", 2)]

        with self.assertRaises(KeyError):
            root_node[("child_not_exist", 1)]

        root_node.close()

    def test_group_attributes(self):
        node = self.open_node(str(self.zarr_ok2))

        root_node = node[0]

        attr = root_node.get_attribute(DrbZarrAttributeNames.READ_ONLY.value)
        self.assertIsInstance(attr, bool)

    def test_group_attributes_fails(self):
        node = self.open_node(str(self.zarr_ok2))

        root_node = node[0]
        with self.assertRaises(DrbException):
            root_node.get_attribute("empty_attr")

    def test_group_parent(self):
        node = self.open_node(str(self.zarr_ok2))

        root_node = node[0]

        self.assertEqual(root_node.parent, node)
        level1 = root_node[0]

        self.assertEqual(level1.parent, root_node)

    def test_group_value(self):
        node = self.open_node(str(self.zarr_ok2))

        root_node = node[0]

        self.assertEqual(root_node.value, None)

    def test_zarr_without_group(self):
        node = self.open_node(str(self.zarr_without_group))

        root_node = node[0]
        self.assertTrue(isinstance(root_node, DrbZarrArrayNode))

        self.assertFalse(root_node.has_child())

    def test_group_get_children_at(self):
        node = self.open_node(str(self.zarr_ok2))

        root_node = node[0]

        level_node_1 = root_node[0]
        self.assertIsNotNone(level_node_1)
        self.assertEqual(level_node_1.name, "agents")

        with self.assertRaises(IndexError):
            root_node[5]
        self.assertEqual(root_node[-2], root_node[len(root_node) - 2])

    def test_group_get_named_children(self):
        node = self.open_node(str(self.zarr_ok2))

        root_node = node[0]

        child3 = root_node[2]
        self.assertIsNotNone(child3)
        self.assertEqual(child3.name, "scenes")

        child_by_name = root_node[child3.name]

        self.assertEqual(child3, child_by_name)

        child_by_name = root_node[child3.name, None, 0]
        self.assertEqual(child3, child_by_name)

        child_by_name = root_node[child3.name, None, -1]
        self.assertEqual(child3, child_by_name)

        child_by_name = root_node[child3.name, None, :][0]
        self.assertEqual(child3, child_by_name)

        with self.assertRaises(IndexError):
            root_node[child3.name, None, 1:][0]

        with self.assertRaises(KeyError):
            root_node[child3.name, None, 1]

    def test_group_impl(self):
        node = self.open_node(str(self.zarr_ok2))

        root_node = node[0]

        self.assertTrue(root_node.has_impl(zarr.hierarchy.Group))

        impl = root_node.get_impl(zarr.hierarchy.Group)

        self.assertIsInstance(impl, zarr.hierarchy.Group)

    def test_dimension_impl_not_supported(self):
        node = self.open_node(str(self.zarr_ok2))

        root_node = node[0]

        self.assertFalse(root_node.has_impl(io.BufferedIOBase))

        with self.assertRaises(DrbNotImplementationException):
            root_node.get_impl(io.BufferedIOBase)
