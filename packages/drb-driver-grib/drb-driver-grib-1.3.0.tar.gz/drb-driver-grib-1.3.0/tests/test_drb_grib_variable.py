import os
import unittest
from pathlib import Path

import numpy
import xarray
from drb.exceptions.core import DrbException
from drb.drivers.file import DrbFileFactory

from drb.drivers.grib import DrbGribArrayNode
from drb.drivers.grib.grib_common import NAMESPACE_GRIB_NODE
from drb.drivers.grib import DrbGribFactory


class TestDrbVaraibleNodeGrib(unittest.TestCase):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))

    grib_fake = current_path / "files" / "fake.nc"
    grib_file = current_path / "files" / 'temp.grib'

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
        self.node = DrbGribFactory().create(self.node_file)
        return self.node

    def test_variable(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['t']

        self.assertIsInstance(temp_node, DrbGribArrayNode)

    def test_variable_attributes(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['t']

        self.assertIsNotNone(temp_node.get_attribute('GRIB_name', None))
        self.assertEqual(temp_node.get_attribute('GRIB_name', None),
                         'Temperature')

        with self.assertRaises(DrbException):
            self.assertIsNotNone(temp_node.get_attribute('toto', None))

    def test_variable_parent(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['t']

        self.assertEqual(temp_node.parent, node)

    def test_variable_has_impl(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['t']
        print(temp_node)
        self.assertTrue(temp_node.has_impl(xarray.DataArray))
        self.assertTrue(temp_node.has_impl(numpy.ndarray))

    def test_variable_get_impl(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['t']

        impl = temp_node.get_impl(xarray.DataArray)
        self.assertIsInstance(impl, xarray.DataArray)

        impl = temp_node.get_impl(numpy.ndarray)
        self.assertIsInstance(impl, numpy.ndarray)

    def test_variable_impl_not_supported(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['t']

        self.assertFalse(temp_node.has_impl(xarray.Dataset))

        with self.assertRaises(DrbException):
            self.assertIsNotNone(temp_node.get_impl(xarray.Dataset))

    def test_variable_namespace_uri(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['t']

        self.assertEqual(temp_node.namespace_uri, NAMESPACE_GRIB_NODE)

    def test_variable_children(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node[0]
        self.assertEqual(len(temp_node.children), 0)

    def test_variable_value(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['t']

        self.assertIsInstance(temp_node.value, xarray.DataArray)

    def test_variable_close(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['t']

        temp_node.close()
