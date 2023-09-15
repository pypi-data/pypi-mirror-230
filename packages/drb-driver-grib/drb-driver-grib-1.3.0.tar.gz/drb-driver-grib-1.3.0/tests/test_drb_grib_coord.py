import os
import unittest
from pathlib import Path

import xarray
from drb.drivers.file import DrbFileFactory
from drb.exceptions.core import DrbException


from drb.drivers.grib import DrbGribArrayNode, DrbGribCoordNode
from drb.drivers.grib.grib_common import NAMESPACE_GRIB_NODE
from drb.drivers.grib import DrbGribFactory


class TestDrbCoordinateNodeGrib(unittest.TestCase):
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

    def test_coord(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['coordinates']

        self.assertIsInstance(temp_node, DrbGribCoordNode)

    def test_coord_attributes(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['coordinates']

        self.assertEqual(temp_node.attributes, {})

        with self.assertRaises(DrbException):
            self.assertIsNotNone(temp_node.get_attribute('toto', None))

    def test_coord_parent(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['coordinates']

        self.assertEqual(temp_node.parent, node)

    def test_coord_has_impl(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['coordinates']

        self.assertTrue(temp_node.has_impl(
            xarray.core.coordinates.DatasetCoordinates))

    def test_coord_get_impl(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['coordinates']

        impl = temp_node.get_impl(xarray.core.coordinates.DatasetCoordinates)
        self.assertIsInstance(impl,
                              xarray.core.coordinates.DatasetCoordinates)

    def test_coord_impl_not_supported(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['coordinates']

        self.assertFalse(temp_node.has_impl(xarray.Dataset))

        with self.assertRaises(DrbException):
            self.assertIsNotNone(temp_node.get_impl(xarray.Dataset))

    def test_coord_namespace_uri(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['coordinates']

        self.assertEqual(temp_node.namespace_uri, NAMESPACE_GRIB_NODE)

    def test_coord_children(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['coordinates']
        self.assertTrue(len(temp_node.children) > 1)

    def test_coord_child(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['coordinates']

        self.assertTrue(temp_node.has_child('longitude'))
        self.assertIsNotNone(temp_node['longitude'])

        self.assertIsInstance(temp_node['longitude'], DrbGribArrayNode)

    def test_variable_value(self):
        node = self.open_node(str(self.grib_file))

        temp_node = node['coordinates']

        self.assertIsInstance(temp_node.value,
                              xarray.core.coordinates.DatasetCoordinates)
