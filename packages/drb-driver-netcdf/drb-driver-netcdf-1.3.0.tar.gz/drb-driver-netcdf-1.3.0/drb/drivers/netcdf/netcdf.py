import enum
from abc import ABC
from typing import List, Any
import netCDF4 as netCDF
import numpy
import xarray

from deprecated.classic import deprecated
from drb.core import DrbNode
from drb.nodes.abstract_node import AbstractNode
from drb.topics import resolver


class DrbNetcdfAttributeNames(enum.Enum):
    UNLIMITED = 'unlimited'
    """
    A boolean indicating whether the netcdf file has a fixed size or not.
    """


class DrbNetcdfSimpleNode(AbstractNode, ABC):
    """
    This node will be inherited by DrbNetcdfSimpleValueNode
    and DrbNetcdfDimensionNode.

    It is used to represent the key to a node with value.

    Parameters:
        parent (DrbNode): The parent of the node.
        name (str): the name of the node.
    """

    def __init__(self, parent: DrbNode, name):
        super().__init__()
        self.parent: DrbNode = parent
        self.name = name

    @property
    @deprecated(version='1.2.0',
                reason='Usage of the bracket is recommended')
    def children(self) -> List[DrbNode]:
        """
        This node as no children.

        Returns:
            List: An empty List
        """
        return []

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError


class DrbNetcdfSimpleValueNode(DrbNetcdfSimpleNode):
    """
    This node is used to get a simple value.

    Parameters:
        parent (DrbNode): The parent of the node.
        name (str): the name of the node.
        value (any): the value.
    """
    def __init__(self, parent: DrbNode, name: str, value: any):
        super().__init__(parent, name)
        self.value = value


class DrbNetcdfDimensionNode(DrbNetcdfSimpleNode):
    """
    This node is used to retrieve the dimension of a netcdf.
    A netCDF `Dimension` is used to describe the coordinates of a `Variable`.
    The value of the file is his dimension only if it is not UNLIMITED.

    Parameters:
        parent (DrbNode): The parent of the node.
        dimension (netCDF.Dimension): the dimension of the netcdf.
    """

    @staticmethod
    def __to_netcdf_dimension(node: DrbNode, **kwargs):
        if isinstance(node, DrbNetcdfDimensionNode):
            return node._dimension
        raise TypeError(f'invalid given node {node.__class__}')

    def __init__(self, parent: DrbNode, dimension: netCDF.Dimension):
        super().__init__(parent, dimension.name)
        self._dimension = dimension
        if self.value is None:
            if self._dimension.isunlimited():
                self.value = -1
            else:
                self.value = self._dimension.size
        self.__init_attributes()
        self.add_impl(netCDF.Dimension, self.__to_netcdf_dimension)

    def __init_attributes(self):
        """
        The attributes of this node only contain UNLIMITED a boolean,
        True if the netcdf has no limit otherwise False.
        """
        self @= (DrbNetcdfAttributeNames.UNLIMITED.value,
                 self._dimension.isunlimited())


class DrbNetcdfGroupNode(AbstractNode):
    """
    The DrbNetcdfGroupNode is used to organize data inside a netcdf file.

    The DrbNetcdfGroupNode can contain:

            **dimensions**: The `dimensions` dictionary maps the names of
            dimensions defined for the `Group` or `Dataset` to instances of the
            `Dimension` class.

            **variables**: The `variables` dictionary maps the names of
            variables defined for this `Dataset` or `Group` to instances
            of the `Variable` class.

            **groups**: The groups dictionary maps the names of groups created
            for this `Dataset` or `Group` to instances of the `Group` class
            (the `Dataset` class is simply a special case of the `Group` class
            which describes the root group in the netCDF4 file).

    Parameters:
        parent(DrbNode): The parent of the node.
        data_set(netCDF.Dataset):The dataset of the netcdf.
    """

    @staticmethod
    def __to_netcdf_dataset(node: DrbNode, **kwargs):
        if isinstance(node, DrbNetcdfGroupNode):
            return node._data_set
        raise TypeError(f'invalid given node {node.__class__}')

    @staticmethod
    def __to_xarray_dataset(node: DrbNode, **kwargs):
        if isinstance(node, DrbNetcdfGroupNode):
            store = xarray.backends.NetCDF4DataStore(node._data_set)
            return xarray.open_dataset(store)
        raise TypeError(f'invalid given node {node.__class__}')

    def __init__(self, parent: DrbNode, data_set: netCDF.Dataset):
        super().__init__()

        name = data_set.name
        if name == '/':
            name = 'root'
        self.name = name
        self.parent: DrbNode = parent
        self._children: List[DrbNode] = None
        self._data_set = data_set
        self.add_impl(netCDF.Dataset, self.__to_netcdf_dataset)
        self.add_impl(xarray.Dataset, self.__to_xarray_dataset)
        self.__init_attributes()

    def __init_attributes(self):
        for attribute_name in self._data_set.ncattrs():
            data = (attribute_name, getattr(self._data_set, attribute_name))
            self.__imatmul__(data)

    @property
    @deprecated(version='1.2.0',
                reason='Usage of the bracket is recommended')
    @resolver.resolve_children
    def children(self) -> List[DrbNode]:
        if self._children is None:
            self._children = []
            dimensions = self._data_set.dimensions
            if dimensions is not None and len(dimensions) > 0:
                nodelist = DrbNetcdfListNode(self, 'dimensions')
                for dim in dimensions:
                    nodelist.append_child(
                        DrbNetcdfDimensionNode(nodelist, dimensions[dim]))
                self._children.append(nodelist)

            variables = self._data_set.variables
            if variables is not None and len(variables) > 0:
                nodelist = DrbNetcdfListNode(self, 'variables')
                for variable in variables:
                    nodelist.append_child(
                        DrbNetcdfVariableNode(nodelist, variables[variable]))
                self._children.append(nodelist)

            groups = self._data_set.groups
            for grp in groups.values():
                self._children.append(DrbNetcdfGroupNode(self, grp))
        return self._children

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError


class DrbNetcdfListNode(AbstractNode):
    """
    This node is used to have one or many children of DrbNode but no value.

    Parameters:
        parent (DrbNode): The node parent.
        name (str): the name of the data.
    """
    def __init__(self, parent: DrbNode, name: str):
        super().__init__()
        self.name = name
        self.parent: DrbNode = parent
        self._children: List[DrbNode] = []

    @property
    @deprecated(version='1.2.0',
                reason='Usage of the bracket is recommended')
    @resolver.resolve_children
    def children(self) -> List[DrbNode]:
        return self._children

    def append_child(self, node: DrbNode) -> None:
        """
        Appends a DrbNode giving in argument to the list of children.

        Parameters:
            node (DrbNode): The node to add.
        """
        self._children.append(node)

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError


class DrbNetcdfVariableNode(AbstractNode):
    """
    This node is used to retrieve the variable of a netcdf.
    A netCDF `Variable` is used to read and write netCDF data.

    Parameters:
        parent (DrbNode): The parent of the node.
        variable (netCDF.Variable): the variable of the netcdf.
    """

    @staticmethod
    def __to_netcdf_variable(node: DrbNode, **kwargs):
        if isinstance(node, DrbNetcdfVariableNode):
            return node._variable
        raise TypeError(f'invalid given node {node.__class__}')

    @staticmethod
    def __to_xarray_data_array(node: DrbNode, **kwargs):
        if isinstance(node, DrbNetcdfVariableNode):
            grand_parent = node.parent.parent
            if grand_parent and grand_parent.has_impl(xarray.Dataset):
                xarray_dataset = grand_parent.get_impl(xarray.Dataset)
                return xarray_dataset[node.name]
            raise RuntimeError('Unsupported implementation: xarray.DataArray')
        raise TypeError(f'invalid given node {node.__class__}')

    @staticmethod
    def __to_numpy_nd_array(node: DrbNode, **kwargs):
        if isinstance(node, DrbNetcdfVariableNode):
            if node._is_scalar:
                node._variable.set_auto_mask(False)
                array_to_return = node._variable[:]
                node._variable.set_auto_mask(True)
                return array_to_return
            return node._variable[:]
        raise TypeError(f'invalid given node {node.__class__}')

    def __init__(self, parent: DrbNode, variable: netCDF.Variable):
        super().__init__()

        self.name = variable.name
        self.parent: DrbNode = parent
        self._children: List[DrbNode] = None
        self._variable = variable
        # value scalar indicate a variable with only one value
        # in this case value return this value
        # and all method to retrieve array are not activated
        # this type of variable can be for example a time...
        self._is_scalar = len(self._variable.shape) == 0

        self.add_impl(netCDF.Variable, self.__to_netcdf_variable)
        self.add_impl(xarray.DataArray, self.__to_xarray_data_array)
        if not self._is_scalar:
            self.add_impl(numpy.ndarray, self.__to_numpy_nd_array)
            if variable.mask:
                self.add_impl(numpy.ma.masked_array, self.__to_numpy_nd_array)

        self.__init_attributes()
        if self._is_scalar:
            self.value = self._variable.getValue()

    def __init_attributes(self):
        for attribute_name in self._variable.ncattrs():
            self @= (attribute_name, getattr(
                self._variable, attribute_name))

    @property
    @deprecated(version='1.2.0',
                reason='Usage of the bracket is recommended')
    def children(self) -> List[DrbNode]:

        if self._children is None:
            self._children = []
            if not self._is_scalar:
                self._children.append(DrbNetcdfSimpleValueNode(
                    self, 'dimensions', self._variable.dimensions))
                self._children.append(DrbNetcdfSimpleValueNode(
                    self, 'shape', self._variable.shape))
            self._children.append(DrbNetcdfSimpleValueNode(
                self, 'size', self._variable.size))
        return self._children

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError
