import os
import unittest
from pathlib import Path
import io

from drb.exceptions.core import DrbException
from drb.drivers.file import DrbFileFactory

from drb.drivers.zarr import DrbZarrNode, DrbZarrFactory


class TestDrbNodeFactoryZarr(unittest.TestCase):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))

    zarr_fake = current_path / "files" / "fake.zarr"

    zarr_ok2 = current_path / "files" / "sample.zarr"
    zarr_without_group = current_path / "files" / "example.zarr"
    empty_file = current_path / "files" / "empty.files"

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

    def test_opened_file_node(self):
        node = self.open_node(str(self.zarr_ok2))

        self.assertIsInstance(node, DrbZarrNode)
        self.assertEqual(node.name, self.node_file.name)
        self.assertEqual(node.namespace_uri, self.node_file.namespace_uri)

    def test_base_node(self):
        node = self.open_node(str(self.zarr_ok2))

        self.assertEqual(node.parent, self.node_file.parent)
        self.assertEqual(node.value, self.node_file.value)

        self.assertIsInstance(node, DrbZarrNode)

        self.assertEqual(len(node), 1)
        self.assertTrue(node.has_child())

    def test_base_node_get_child(self):
        node = self.open_node(str(self.zarr_ok2))

        self.assertEqual(node[0].name, ".")
        self.assertEqual(node["."].name, ".")
        self.assertEqual(node[".", :][0].name, ".")
        self.assertEqual(node[".", -1].name, ".")

        with self.assertRaises(IndexError):
            node[".", 1:][0]
            node[".", :][1]

        self.assertEqual(len(node.children), 1)

    def test_base_node_has_child(self):
        node = self.open_node(str(self.zarr_ok2))

        self.assertTrue(node.has_child())
        self.assertTrue(node.has_child("."))
        self.assertTrue(node.has_child(".", None))
        self.assertFalse(node.has_child(".", "empty"))
        self.assertFalse(node.has_child("empty"))

    def test_base_node_attribute(self):
        node = self.open_node(str(self.zarr_ok2))

        self.assertEqual(node.attributes, self.node_file.attributes)

        self.assertEqual(
            node.get_attribute('mode'),
            self.node_file.get_attribute('mode'),
        )

    def test_base_node_impl(self):
        node = self.open_node(str(self.zarr_ok2))

        impl_base_file = io.BufferedIOBase

        # because it is directory no impl
        self.assertEqual(
            node.has_impl(impl_base_file),
            self.node_file.has_impl(impl_base_file)
        )

        with self.assertRaises(Exception):
            node.get_impl(impl_base_file)

    def test_path(self):
        node = self.open_node(str(self.zarr_ok2))

        root_node = node[0]

        self.assertEqual(root_node.path.path, node.path.path + "/.")

    def test_fake(self):
        node = self.open_node(str(self.zarr_fake))

        self.assertEqual(node.name, "fake.zarr")

        with self.assertRaises(DrbException):
            len(node)
