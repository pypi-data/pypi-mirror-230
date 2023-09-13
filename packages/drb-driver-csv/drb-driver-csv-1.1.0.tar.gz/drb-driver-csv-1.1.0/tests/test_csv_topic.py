from drb.topics.topic import TopicCategory
from drb.topics.dao import ManagerDao
from drb.nodes.logical_node import DrbLogicalNode
import unittest
import uuid
import os
import drb.topics.resolver as resolver


class TestCsvTopic(unittest.TestCase):
    topic_uuid = uuid.UUID('c03d4f6b-d147-4eeb-8433-72fcdabbef9f')

    def test_check_base_info(self):
        topic = ManagerDao().get_drb_topic(self.topic_uuid)
        self.assertIsNotNone(topic)
        self.assertEqual('CSV', topic.label)
        self.assertEqual('Comma-Separated Values', topic.description)
        self.assertEqual(TopicCategory.FORMATTING, topic.category)
        self.assertEqual('csv', topic.factory)

    def test_topic_signature(self):
        topic = ManagerDao().get_drb_topic(self.topic_uuid)
        node = DrbLogicalNode('foobar.csv')
        self.assertTrue(topic.matches(node))

        node = DrbLogicalNode('foobar')
        node @= ('Content-Type', 'text/csv')
        self.assertTrue(topic.matches(node))

        node = DrbLogicalNode('foobar')
        self.assertFalse(topic.matches(node))

    def test_topic_via_resolver(self):
        resource_dir = os.path.join(os.path.dirname(__file__), 'resources')
        path = os.path.join(resource_dir, 'nuts_area_2021.csv')
        topic, _ = resolver.resolve(path)
        self.assertEqual(self.topic_uuid, topic.id)
