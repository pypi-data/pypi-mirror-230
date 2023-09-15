import io
import os
import unittest
from pathlib import Path

import xarray
from drb.exceptions.core import DrbException
from drb.drivers.file import DrbFileFactory

from drb.drivers.grib import DrbGribDimNode
from drb.drivers.grib.grib_common import NAMESPACE_GRIB_NODE, \
    DrbGribSimpleValueNode
from drb.drivers.grib import DrbGribFactory


class TestDrbDimensionNodeGrib(unittest.TestCase):
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

    def test_dim(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['dimensions']

        self.assertIsInstance(temp_node, DrbGribDimNode)

    def test_dim_attributes(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['dimensions']

        self.assertEqual(temp_node.attributes, {})

        with self.assertRaises(DrbException):
            self.assertIsNotNone(temp_node.get_attribute('toto', None))

    def test_dim_parent(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['dimensions']

        self.assertEqual(temp_node.parent, node)

    def test_dim_impl_not_supported(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['dimensions']

        self.assertFalse(temp_node.has_impl(xarray.Dataset))

        with self.assertRaises(DrbException):
            self.assertIsNotNone(temp_node.get_impl(xarray.Dataset))

    def test_dim_namespace_uri(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['dimensions']

        self.assertEqual(temp_node.namespace_uri, NAMESPACE_GRIB_NODE)

    def test_dim_value(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['dimensions']
        self.assertIsNone(temp_node.value)

    def test_dim_children(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['dimensions']
        self.assertTrue(len(temp_node.children) > 1)

    def test_dim_child(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['dimensions']

        self.assertTrue(temp_node.has_child('longitude'))
        self.assertIsNotNone(temp_node['longitude'])

        self.assertIsInstance(temp_node['longitude'], DrbGribSimpleValueNode)

    def test_dim_child_longitude(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['dimensions']

        node_long = temp_node['longitude']

        self.assertEqual(node_long.value, 1440)

    def test_dim_child_longitude_parent(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['dimensions']

        node_long = temp_node['longitude']

        self.assertEqual(node_long.parent, temp_node)

    def test_dim_child_longitude_name(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['dimensions']

        node_long = temp_node['longitude']

        self.assertEqual(node_long.name, 'longitude')

    def test_dim_child_longitude_path(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['dimensions']

        node_long = temp_node['longitude']

        self.assertEqual(node_long.path.name,
                         Path(temp_node.path.name).joinpath('longitude').
                         as_posix())

    def test_dim_child_longitude_attributes(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['dimensions']

        node_long = temp_node['longitude']

        self.assertEqual(node_long.attributes, {})
        with self.assertRaises(DrbException):
            self.assertIsNotNone(node_long.get_attribute('', None))

    def test_dim_child_longitude_impl(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['dimensions']

        node_long = temp_node['longitude']

        self.assertFalse(node_long.has_impl(io.BytesIO))
        with self.assertRaises(DrbException):
            self.assertIsNotNone(node_long.get_impl(io.BytesIO))

    def test_dim_child_longitude_children(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['dimensions']

        node_long = temp_node['longitude']

        self.assertEqual(len(node_long), 0)
        self.assertEqual(len(node_long.children), 0)
