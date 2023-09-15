import os
import unittest
from pathlib import Path

import zarr.hierarchy
from drb.exceptions.core import DrbNotImplementationException, DrbException
from drb.drivers.file import DrbFileFactory

from drb.drivers.zarr import DrbZarrFactory
from drb.drivers.zarr.zarr_data_set_node import DrbZarrArrayNode


class TestDrbGroupNodeZarr(unittest.TestCase):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))

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

    def test_array_parent(self):
        node = self.open_node(str(self.zarr_ok2))

        root_node = node[0]
        second_child = root_node[1]

        self.assertEqual(second_child.parent, root_node)

    def test_array_has_no_child(self):
        node = self.open_node(str(self.zarr_without_group))

        root_node = node[0]
        self.assertTrue(isinstance(root_node, DrbZarrArrayNode))

        self.assertFalse(root_node.has_child())
        self.assertFalse(root_node.has_child("toto", "ns"))

        self.assertEqual(len(root_node), 0)

    def test_array_get_children_at(self):
        node = self.open_node(str(self.zarr_ok2))

        root_node = node[0]
        second_child = root_node[1]

        with self.assertRaises(IndexError):
            second_child[0]

    def test_array_impl(self):
        node = self.open_node(str(self.zarr_without_group))

        root_node = node[0]

        self.assertTrue(root_node.has_impl(zarr.core.Array))

        impl = root_node.get_impl(zarr.core.Array)

        self.assertIsInstance(impl, zarr.core.Array)

    def test_dimension_impl_not_supported(self):
        node = self.open_node(str(self.zarr_without_group))

        root_node = node[0]

        self.assertFalse(root_node.has_impl(zarr.hierarchy.Group))

        with self.assertRaises(DrbNotImplementationException):
            root_node.get_impl(zarr.hierarchy.Group)

    def test_array_attributes(self):
        node = self.open_node(str(self.zarr_without_group))

        root_node = node[0]

        attr = root_node.get_attribute("myattr")
        self.assertEqual(attr, "myattr_value")

    def test_array_attributes_fails(self):
        node = self.open_node(str(self.zarr_without_group))

        root_node = node[0]
        with self.assertRaises(DrbException):
            root_node.get_attribute("empty_attr")
