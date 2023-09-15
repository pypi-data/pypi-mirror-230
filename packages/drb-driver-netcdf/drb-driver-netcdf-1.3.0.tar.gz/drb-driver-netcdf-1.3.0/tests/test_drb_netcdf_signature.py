import os
import unittest
import uuid
from pathlib import Path

from drb.core.factory import FactoryLoader
from drb.nodes.logical_node import DrbLogicalNode
from drb.topics.dao import ManagerDao
from drb.topics.topic import TopicCategory

from drb.drivers.netcdf import DrbNetcdfFactory


class TestDrbNetcdfSignature(unittest.TestCase):
    mock_pkg = None
    fc_loader = None
    topic_loader = None
    netcdf_id = uuid.UUID('83720abe-2c0e-11ec-8d3d-0242ac130003')
    hdf5_id = uuid.UUID('b4e6ba07-3a59-4736-b33d-3c55dcae2c56')

    current_path = Path(os.path.dirname(os.path.realpath(__file__)))
    netcdf_with_one_group = current_path / "files" / 'sgpsondewnpnC1.nc'
    path_hdf5 = current_path / "files" / 'test.hdf5'

    empty_file = current_path / "files" / "empty.file"

    @classmethod
    def setUpClass(cls) -> None:
        cls.fc_loader = FactoryLoader()
        cls.topic_loader = ManagerDao()

    def test_impl_loading(self):
        factory_name = 'netcdf'

        factory = self.fc_loader.get_factory(factory_name)
        self.assertIsNotNone(factory)
        self.assertIsInstance(factory, DrbNetcdfFactory)

        topic = self.topic_loader.get_drb_topic(self.netcdf_id)
        self.assertIsNotNone(factory)
        self.assertEqual(self.netcdf_id, topic.id)
        self.assertEqual('netCDF', topic.label)
        self.assertIsNone(topic.description)
        self.assertEqual(TopicCategory.FORMATTING, topic.category)
        self.assertEqual(factory_name, topic.factory)

    def test_impl_signatures(self):
        topic = self.topic_loader.get_drb_topic(self.netcdf_id)

        node = DrbLogicalNode(self.netcdf_with_one_group)
        self.assertTrue(topic.matches(node))

        node = DrbLogicalNode(self.empty_file)
        self.assertFalse(topic.matches(node))

    def test_hdf5(self):
        topic = self.topic_loader.get_drb_topic(self.hdf5_id)

        node = DrbLogicalNode(self.path_hdf5)
        self.assertTrue(topic.matches(node))
