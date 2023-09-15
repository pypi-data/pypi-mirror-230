import copy
import io
import os
import tempfile
from typing import Any, List, Dict, Tuple, Optional


from drb.nodes.abstract_node import AbstractNode
from drb.drivers.file import DrbFileNode
from drb.core import DrbNode, ParsedPath, DrbFactory

import xarray

from drb.exceptions.grib import DrbGribNobeException
from drb.drivers.grib import DrbGribCoordNode, DrbGribArrayNode, \
    DrbGribDimNode
from drb.exceptions.core import DrbException


class DrbGribNode(AbstractNode):
    """
    This node is used to instantiate a DrbGribNode from another
    implementation of drb such as file.


    Parameters:
        base_node (DrbNode): the base node of this node.
    """
    def __init__(self, base_node: DrbNode):
        super().__init__()

        grib_file_source = None
        self._root_dataset = None
        self._attributes = None
        self._children = None
        self.base_node = base_node
        self.temp_file = False
        self._filename = None
        self._impl_mng = copy.copy(base_node._impl_mng)
        self.add_impl(xarray.Dataset, self._to_xarray_dataset)
        if isinstance(self.base_node, DrbFileNode):
            grib_file_source = self.base_node.get_impl(io.BufferedIOBase)
        else:
            if self.base_node.has_impl(io.BufferedIOBase):
                stream_io = self.base_node.get_impl(io.BufferedIOBase)
                grib_file_source = tempfile.NamedTemporaryFile(delete=False)
                grib_file_source.write(stream_io.read())
                grib_file_source.close()
                stream_io.close()
                self.temp_file = True
        if grib_file_source.name is not None:
            self._filename = grib_file_source.name
            self._root_dataset = xarray.open_dataset(
                self._filename,
                engine="cfgrib")
        else:
            raise DrbGribNobeException('Unsupported base node '
                                       f'{type(self.base_node).__name__}'
                                       ' for DrbGribNode')

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
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        if self._attributes is None:
            self._attributes = {}

            if self._root_dataset is not None and \
                    self._root_dataset.attrs is not None:
                for key in self._root_dataset.attrs:
                    self._attributes[(key, None)] = \
                        self._root_dataset.attrs[key]

            self._attributes.update(self.base_node.attributes)
        return self._attributes

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        key = (name, namespace_uri)
        if key in self.attributes.keys():
            return self.attributes[key]
        raise DrbException(f'Attribute not found name: {name}, '
                           f'namespace: {namespace_uri}')

    @property
    def children(self) -> List[DrbNode]:
        if self._children is None:
            self._children = []
            for key in self._root_dataset.data_vars.keys():
                self._children.append(
                    DrbGribArrayNode(self,
                                     str(key),
                                     self._root_dataset.data_vars[key]))
            if self._root_dataset.coords is not None:
                self._children.append(
                    DrbGribCoordNode(self, self._root_dataset.coords))
            if self._root_dataset.dims is not None:
                self._children.append(
                    DrbGribDimNode(self, self._root_dataset.dims))

        return self._children

    @staticmethod
    def _to_xarray_dataset(node: DrbNode, **kwargs) -> xarray.Dataset:
        if isinstance(node, DrbGribNode):
            return node._root_dataset
        raise TypeError(f'Invalid node type: {type(node)}')

    def close(self):
        if self._root_dataset is not None:
            self._root_dataset.close()
        if self.temp_file and self._filename is not None:
            os.remove(self._filename)

        self.base_node.close()


class DrbGribFactory(DrbFactory):

    def _create(self, node: DrbNode) -> DrbNode:
        if isinstance(node, DrbGribNode):
            return node
        return DrbGribNode(base_node=node)
