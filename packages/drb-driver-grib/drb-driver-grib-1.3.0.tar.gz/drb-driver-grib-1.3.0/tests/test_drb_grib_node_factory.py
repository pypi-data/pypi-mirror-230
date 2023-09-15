import os
import unittest
from pathlib import Path
import io


from drb.drivers.file import DrbFileFactory

from drb.drivers.grib import DrbGribFactory, DrbGribNode

import xarray

GROUP_NOT_EXIST = "fake_group"


class TestDrbNodeFactoryGrib(unittest.TestCase):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))

    grib_fake = current_path / "files" / "fake.grib"
    grib_file = current_path / "files" / 'temp.grib'

    def open_node(self, path_file):
        self.node_file = DrbFileFactory().create(path_file)
        self.node = DrbGribFactory().create(self.node_file)
        return self.node

    def test_opened_file_node(self):
        node = self.open_node(str(self.grib_file))

        self.assertIsInstance(node, DrbGribNode)
        self.assertEqual(node.name, self.node_file.name)
        self.assertEqual(node.namespace_uri, self.node_file.namespace_uri)

    def test_base_node(self):
        node = self.open_node(str(self.grib_file))

        self.assertEqual(node.parent, self.node_file.parent)
        self.assertEqual(node.value, self.node_file.value)

        self.assertIsInstance(node, DrbGribNode)

        self.assertTrue(node.has_child())

    def test_base_node_has_child(self):
        node = self.open_node(str(self.grib_file))

        self.assertTrue(node.has_child('coordinates'))
        self.assertTrue(node.has_child('dimensions'))

        self.assertEqual(len(node.children), 3)

    def test_base_node_get_child(self):
        node = self.open_node(str(self.grib_file))

        self.assertIsNotNone(node['coordinates'])
        self.assertIsNotNone(node[0])

        self.assertEqual(len(node.children), 3)

    def test_base_node_attribute(self):
        node = self.open_node(str(self.grib_file))

        for key in self.node_file.attributes.keys():
            self.assertEqual(node.get_attribute(key[0]),
                             self.node_file.get_attribute(key[0]))

        self.assertTrue(('GRIB_subCentre', None) in node.attributes.keys())

    def test_base_node_impl(self):
        node = self.open_node(str(self.grib_file))

        impl_base_file = io.BufferedIOBase

        self.assertTrue(node.has_impl(impl_base_file))

        impl = node.get_impl(impl_base_file)
        self.assertIsNotNone(impl)
        self.assertIsInstance(impl, impl_base_file)

    def test_node_impl(self):
        node = self.open_node(str(self.grib_file))

        self.assertTrue(node.has_impl(xarray.Dataset))

        impl = node.get_impl(xarray.Dataset)
        self.assertIsNotNone(impl)
        self.assertIsInstance(impl, xarray.Dataset)

    def test_path(self):
        node = self.open_node(str(self.grib_file))

        self.assertEqual(node.path.path, Path(self.grib_file).as_posix())
