from . import _version
from .netcdf import (
    DrbNetcdfGroupNode, DrbNetcdfVariableNode,
    DrbNetcdfAttributeNames, DrbNetcdfListNode,
    DrbNetcdfDimensionNode, DrbNetcdfSimpleValueNode)

from .netcdf_node_factory import DrbNetcdfFactory, DrbNetcdfNode

__version__ = _version.get_versions()['version']


del _version

__all__ = [
    'DrbNetcdfNode',
    'DrbNetcdfFactory',
    'DrbNetcdfGroupNode',
    'DrbNetcdfVariableNode',
    'DrbNetcdfAttributeNames',
    'DrbNetcdfListNode',
    'DrbNetcdfDimensionNode',
    'DrbNetcdfSimpleValueNode',
]
