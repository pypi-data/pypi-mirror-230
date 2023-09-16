import os
import sys
import unittest
import uuid

from drb.core.factory import FactoryLoader

from drb.nodes.logical_node import DrbLogicalNode
from drb.topics.dao import ManagerDao
from drb.topics.topic import TopicCategory

from drb.drivers.ftp import DrbFtpFactory


class TestFtpFactory(unittest.TestCase):
    fc_loader = None
    ic_loader = None
    ftp_id = uuid.UUID('d61c923a-5f1b-11ec-bf63-0242ac130002')

    @classmethod
    def setUpClass(cls) -> None:
        cls.fc_loader = FactoryLoader()
        cls.topic_loader = ManagerDao()

    def test_impl_loading(self):
        factory_name = 'ftp'

        factory = self.fc_loader.get_factory(factory_name)
        self.assertIsNotNone(factory)
        self.assertIsInstance(factory, DrbFtpFactory)

        topic = self.topic_loader.get_drb_topic(self.ftp_id)
        self.assertIsNotNone(factory)
        self.assertEqual(self.ftp_id, topic.id)
        self.assertEqual('ftp', topic.label)
        self.assertIsNone(topic.description)
        self.assertEqual(TopicCategory.CONTAINER, topic.category)
        self.assertEqual(factory_name, topic.factory)

    def test_impl_signatures(self):
        item_class = self.topic_loader.get_drb_topic(self.ftp_id)

        node = DrbLogicalNode('ftp://localhost:2121/test.txt')
        self.assertTrue(item_class.matches(node))

        node = DrbLogicalNode('sftp://localhost:2121/test.txt')
        self.assertTrue(item_class.matches(node))

        node = DrbLogicalNode('ftps://localhost:2121/test.txt')
        self.assertTrue(item_class.matches(node))

        node = DrbLogicalNode('https://gitlab.com/drb-python')
        self.assertFalse(item_class.matches(node))
