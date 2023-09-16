import os.path
from pathlib import Path
import unittest

from drb.exceptions.core import DrbException

from drb.drivers.swift import SwiftAuth, SwiftService
from tests.utility import start_mock_swift, stop_mock_swift


class TestSwiftContainer(unittest.TestCase):
    node = None
    auth = None
    children = None
    storage_url = "https://my.swift/"
    _os_options = {
        'user_domain_name': 'Default',
        'project_domain_name': 'Default',
        'project_name': 'Default',
        'project_id': 'Default',
        'tenant_name': 'Default',
        'tenant_id': 'Default',
        'region_name': 'SBG'
    }

    @classmethod
    def setUpClass(cls) -> None:
        start_mock_swift(cls.storage_url)
        cls.auth = SwiftAuth(preauthurl=cls.storage_url,
                             preauthtoken="token",
                             auth_version=3, os_options=cls._os_options)
        cls.node = SwiftService(auth=cls.auth)
        cls.children = cls.node['container-1']

    @classmethod
    def tearDownClass(cls) -> None:
        stop_mock_swift()

    def test_name(self):
        self.assertEqual('container-1', self.children.name)

    def test_children(self):
        self.assertIsNotNone(self.children.children)
        self.assertIsInstance(self.children.children, list)
        self.assertEqual(1, len(self.children.children))

    def test_attributes(self):
        self.assertIsNotNone(self.children.attributes)
        self.assertEqual(4, len(self.children.attributes))
        self.assertIsInstance(self.children.attributes, dict)
        swift = {
            ('count', None): 2,
            ('last_modified', None): '2020-11-25T09:37:18.837640',
            ('bytes', None): 2578464,
            ('name', None): 'container-1'
        }
        self.assertEqual(2578464, self.children.get_attribute("bytes"))
        self.assertEqual(2578464, self.children @ "bytes")
        self.assertEqual(swift, self.children.attributes)
        with self.assertRaises(DrbException):
            self.children.get_attribute("something")
        with self.assertRaises(DrbException):
            self.children.get_attribute("swift", "ns")

    def test_parent(self):
        self.assertEqual(self.node, self.children)

    def test_path(self):
        self.assertEqual(
            Path(os.path.sep, 'container-1').as_posix(),
            self.children.path.path)

    def test_impl(self):
        self.assertFalse(self.node.has_impl('impl'))
        with self.assertRaises(DrbException):
            self.node.get_impl('impl')

    def test_has_child(self):
        self.assertTrue(self.children.has_child('test.txt'))
        self.assertTrue(self.children.has_child())
        self.assertFalse(self.children.has_child('container'))
        self.assertFalse(self.children.has_child('test.txt', 'ns'))

    def test_name_space_uri(self):
        self.assertIsNone(self.node.namespace_uri)

    def test_value(self):
        self.assertIsNone(self.node.value)

    def test_auth(self):
        self.assertEqual(self.auth, self.node.get_auth())
