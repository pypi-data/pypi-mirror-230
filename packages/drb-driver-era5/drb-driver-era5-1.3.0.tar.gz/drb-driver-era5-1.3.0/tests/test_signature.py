import os
import sys
import unittest
import uuid

from drb.core.factory import FactoryLoader
from drb.nodes.logical_node import DrbLogicalNode
from drb.topics.dao import ManagerDao
from drb.topics.topic import TopicCategory

from drb.drivers.era5 import Era5Factory


class TestEra5Signature(unittest.TestCase):
    svc_url = 'https+era5://my.domain.com'
    svc_url_false = 'https://my.domain.com'
    fc_loader = None
    topic_loader = None
    era5_id = uuid.UUID('4e34eecd-1fd2-40fb-afb1-01ae4060f66e')

    @classmethod
    def setUpClass(cls) -> None:
        cls.fc_loader = FactoryLoader()
        cls.topic_loader = ManagerDao()

    def test_impl_loading(self):
        factory_name = 'era5'

        factory = self.fc_loader.get_factory(factory_name)
        self.assertIsNotNone(factory)
        self.assertIsInstance(factory, Era5Factory)

        topic = self.topic_loader.get_drb_topic(self.era5_id)
        self.assertIsNotNone(factory)
        self.assertEqual(self.era5_id, topic.id)
        self.assertEqual('Climate Data Store (ERA5)', topic.label)
        self.assertIsNone(topic.description)
        self.assertEqual(TopicCategory.PROTOCOL, topic.category)
        self.assertEqual(factory_name, topic.factory)

    def test_impl_signatures(self):
        topic = self.topic_loader.get_drb_topic(self.era5_id)
        node = DrbLogicalNode(self.svc_url)
        self.assertTrue(topic.matches(node))

        node = DrbLogicalNode(f'{self.svc_url_false}')
        self.assertFalse(topic.matches(node))

        node = DrbLogicalNode(f'http://not.odata.svc')
        self.assertFalse(topic.matches(node))
