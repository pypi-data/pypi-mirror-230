import unittest
import uuid

from drb.core.factory import FactoryLoader
from drb.nodes.logical_node import DrbLogicalNode
from drb.topics.dao import ManagerDao
from drb.topics.topic import TopicCategory

from drb.drivers.discodata import DiscodataFactory


class TestDiscoDataSignature(unittest.TestCase):
    svc_url = 'https+discodata://my.domain.com'
    svc_url_false = 'https://my.domain.com'
    fc_loader = None
    topic_loader = None
    disco_data_id = uuid.UUID('e8d669b6-aa7b-4752-9b1b-72259da25429')

    @classmethod
    def setUpClass(cls) -> None:
        cls.fc_loader = FactoryLoader()
        cls.topic_loader = ManagerDao()

    def test_impl_loading(self):
        factory_name = 'discodata'

        factory = self.fc_loader.get_factory(factory_name)
        self.assertIsNotNone(factory)
        self.assertIsInstance(factory, DiscodataFactory)

        topic = self.topic_loader.get_drb_topic(self.disco_data_id)
        self.assertIsNotNone(factory)
        self.assertEqual(self.disco_data_id, topic.id)
        self.assertEqual('DISCODATA', topic.label)
        self.assertIsNone(topic.description)
        self.assertEqual(TopicCategory.PROTOCOL, topic.category)
        self.assertEqual(factory_name, topic.factory)

    def test_impl_signatures(self):
        topic = self.topic_loader.get_drb_topic(self.disco_data_id)
        node = DrbLogicalNode(self.svc_url)
        self.assertTrue(topic.matches(node))

        node = DrbLogicalNode(f'{self.svc_url_false}')
        self.assertFalse(topic.matches(node))

        node = DrbLogicalNode(f'http://not.odata.svc')
        self.assertFalse(topic.matches(node))
