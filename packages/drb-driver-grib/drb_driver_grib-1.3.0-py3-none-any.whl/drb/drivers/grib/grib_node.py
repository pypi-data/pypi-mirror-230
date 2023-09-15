from typing import Any, List

import numpy

import xarray
import xarray.core.coordinates
from deprecated.classic import deprecated
from drb.core import DrbNode
from drb.exceptions.core import DrbNotImplementationException, DrbException

from drb.drivers.grib.grib_common import DrbGribAbstractNode, \
    DrbGribSimpleValueNode
import drb.topics.resolver as resolver


class DrbGribDimNode(DrbGribAbstractNode):
    """
    This node is used to have one or many children of DrbNode but no value.

    Parameters:
        parent (DrbNode): The node parent.
        dims dimensions (dict like).
    """
    def __init__(self, parent: DrbNode, dims):
        super().__init__(parent, name='dimensions')

        self.parent: DrbNode = parent
        self._children: List[DrbNode] = []
        for key in dims.keys():
            self._children.append(DrbGribSimpleValueNode(self, key, dims[key]))

    @property
    @deprecated(version='1.2.0',
                reason='Usage of the bracket is recommended')
    @resolver.resolve_children
    def children(self) -> List[DrbNode]:
        return self._children


class DrbGribCoordNode(DrbGribAbstractNode):
    """
    This node is used to have one or many children of DrbNode but no value.

    Parameters:
        parent (DrbNode): The node parent.
        data_set_coord (DatasetCoordinates): dataset from xarray.
    """
    def __init__(self, parent: DrbNode,
                 data_set_coord: xarray.core.coordinates.DatasetCoordinates):
        super().__init__(parent, name='coordinates')
        self._data_set_coord = data_set_coord
        self.parent: DrbNode = parent
        self._children = None
        self.add_impl(xarray.core.coordinates.DatasetCoordinates,
                      self._to_xarray_dataset_coordinates)
        self.value = self._data_set_coord

    @property
    @deprecated(version='1.2.0',
                reason='Usage of the bracket is recommended')
    @resolver.resolve_children
    def children(self) -> List[DrbNode]:
        if self._children is None:
            self._children = []
            for key in self._data_set_coord.keys():
                self._children.append(DrbGribArrayNode(
                    self,
                    key,
                    self._data_set_coord[key]))
        return self._children

    @staticmethod
    def _to_xarray_dataset_coordinates(node: DrbNode, **kwargs) \
            -> xarray.core.coordinates.DatasetCoordinates:
        if isinstance(node, DrbGribCoordNode):
            return node._data_set_coord
        raise TypeError(f'Invalid node type: {type(node)}')


class DrbGribArrayNode(DrbGribAbstractNode):
    """
    This node is used to have one or many children of DrbNode but no value.

    Parameters:
        parent (DrbNode): The node parent.
        name (str): the name of the data.
    """
    def __init__(self, parent: DrbNode,
                 name: str,
                 data_array: xarray.DataArray):
        super().__init__(parent, name=name)
        self._data_array = data_array
        self.parent: DrbNode = parent
        self.name = name
        self._attribute = None
        self.add_impl(numpy.ndarray, self._to_numpy_ndarray)
        self.add_impl(xarray.DataArray, self._to_xarray_data_array)
        self.value = data_array.all()
        self.__init_attributes()

    def __init_attributes(self):
        for key in self._data_array.attrs:
            self @= (key, self._data_array.attrs[key])

    @property
    @deprecated(version='1.2.0',
                reason='Usage of the bracket is recommended')
    @resolver.resolve_children
    def children(self) -> List[DrbNode]:
        return []

    @staticmethod
    def _to_numpy_ndarray(node: DrbNode, **kwargs) -> numpy.ndarray:
        if isinstance(node, DrbGribArrayNode):
            return node._data_array.to_numpy()
        raise TypeError(f'Invalid node type: {type(node)}')

    @staticmethod
    def _to_xarray_data_array(node: DrbNode, **kwargs) -> xarray.DataArray:
        if isinstance(node, DrbGribArrayNode):
            return node._data_array
        raise TypeError(f'Invalid node type: {type(node)}')
