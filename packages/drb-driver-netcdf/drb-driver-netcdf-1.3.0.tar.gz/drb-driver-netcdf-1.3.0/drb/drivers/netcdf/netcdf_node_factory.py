import io
import os
import tempfile
from typing import Any, List, Dict, Tuple, Optional

import netCDF4

from drb.nodes.abstract_node import AbstractNode
from drb.drivers.file import DrbFileNode
from drb.core import DrbNode, ParsedPath, DrbFactory

from . import DrbNetcdfGroupNode
from ...exceptions.netcdf import DrbNetcdfNodeException


class DrbNetcdfNode(AbstractNode):
    """
    This node is used to instantiate a DrbNetcdfNode from another
    implementation of drb such as file.


    Parameters:
        base_node (DrbNode): the base node of this node.
    """
    def __init__(self, base_node: DrbNode):
        super().__init__()

        _netcdf_file_source = None
        self._root_dataset = None
        self.base_node = base_node
        self.temp_file = False
        stream_io = None
        if isinstance(self.base_node, DrbFileNode):
            _netcdf_file_source = self.base_node \
                         .get_impl(io.BufferedIOBase)
        else:
            if self.base_node.has_impl(io.BytesIO):
                stream_io = self.base_node.get_impl(io.BytesIO)
            elif self.base_node.has_impl(io.BufferedIOBase):
                stream_io = self.base_node.get_impl(io.BufferedIOBase)

            if stream_io is not None:
                _netcdf_file_source = tempfile.NamedTemporaryFile(delete=False)
                _netcdf_file_source.write(stream_io.read())
                stream_io.close()
                self.temp_file = True
            else:
                raise DrbNetcdfNodeException(f'Unsupported parent '
                                             f'{type(self.base_node).__name__}'
                                             f' for DrbNetcdfRootNode')
        self._filename = _netcdf_file_source.name
        _netcdf_file_source.close()
        self._root_node = None

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
        return self.base_node.attributes

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        return self.base_node.get_attribute(name, namespace_uri)

    @property
    def children(self) -> List[DrbNode]:
        if self._root_node is None:
            self._root_dataset = netCDF4.Dataset(filename=self._filename)
            self._root_node = DrbNetcdfGroupNode(self, self._root_dataset)
        return [self._root_node]

    def has_impl(self, impl: type) -> bool:
        return self.base_node.has_impl(impl)

    def get_impl(self, impl: type, **kwargs) -> Any:
        return self.base_node.get_impl(impl)

    def close(self):
        if self._root_dataset is not None:
            self._root_dataset.close()
        if self.temp_file:
            os.remove(self._filename)
        self.base_node.close()


class DrbNetcdfFactory(DrbFactory):

    def _create(self, node: DrbNode) -> DrbNode:
        if isinstance(node, DrbNetcdfNode):
            return node
        return DrbNetcdfNode(base_node=node)
