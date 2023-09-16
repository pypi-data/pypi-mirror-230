import os.path
from pathlib import Path
import unittest

from drb.exceptions.core import DrbException

from drb.drivers.swift import SwiftAuth, SwiftService
from tests.utility import start_mock_swift, stop_mock_swift


class TestSwiftService(unittest.TestCase):
    node = None
    auth = None
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

    @classmethod
    def tearDownClass(cls) -> None:
        stop_mock_swift()

    def test_name(self):
        self.assertEqual(self.storage_url, self.node.name)

    def test_children(self):
        self.assertIsNotNone(self.node.children)
        self.assertIsInstance(self.node.children, list)
        self.assertEqual(2, len(self.node.children))

    def test_attributes(self):
        self.assertIsNotNone(self.node.attributes)
        self.assertEqual(6, len(self.node.attributes))
        self.assertIsInstance(self.node.attributes, dict)
        swift = {'max_file_size': 5368709122, 'account_listing_limit': 10000}
        self.assertEqual(swift, self.node.get_attribute("swift"))
        with self.assertRaises(DrbException):
            self.node.get_attribute("something")
        with self.assertRaises(DrbException):
            self.node.get_attribute("swift", "ns")

    def test_parent(self):
        self.assertIsNone(self.node.parent)

    def test_path(self):
        self.assertEqual(
                        Path(os.path.sep).as_posix(),
                        self.node.path.path)

    def test_impl(self):
        self.assertFalse(self.node.has_impl('impl'))
        with self.assertRaises(DrbException):
            self.node.get_impl('impl')

    def test_has_child(self):
        self.assertTrue(self.node.has_child('container-1'))
        self.assertTrue(self.node.has_child())
        self.assertFalse(self.node.has_child('container'))
        self.assertFalse(self.node.has_child('container-1', 'ns'))

    def test_name_space_uri(self):
        self.assertIsNone(self.node.namespace_uri)

    def test_value(self):
        self.assertIsNone(self.node.value)

    def test_auth(self):
        self.assertEqual(self.auth, self.node.get_auth())
