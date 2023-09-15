import os
import unittest
from pathlib import Path


from drb.drivers.netcdf import DrbNetcdfFactory, DrbNetcdfGroupNode, \
    DrbNetcdfVariableNode
from drb.drivers.file import DrbFileFactory


GROUP_ROOT = "root"


class TestDrbNodeNetcdfHdf5(unittest.TestCase):
    current_path = Path(os.path.dirname(os.path.realpath(__file__)))
    path_hdf5 = current_path / "files" / 'test.hdf5'

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
        self.node = DrbNetcdfFactory().create(self.node_file)
        return self.node

    def test_first_group(self):
        node = self.open_node(str(self.path_hdf5))

        root_node = node[0]

        self.assertIsInstance(root_node, DrbNetcdfGroupNode)
        self.assertEqual(root_node.name, GROUP_ROOT)
        self.assertEqual(root_node.namespace_uri, None)

    def test_first_var(self):
        node = self.open_node(str(self.path_hdf5))

        var_node = node[0]['variables'][0]

        self.assertIsInstance(var_node, DrbNetcdfVariableNode)

        self.assertEqual(var_node.name, 'default')
