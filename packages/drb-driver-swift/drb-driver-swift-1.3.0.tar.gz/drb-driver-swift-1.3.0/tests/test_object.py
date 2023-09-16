import io
import os.path
import unittest
from pathlib import Path

from drb.core import DrbNode
from drb.exceptions.core import DrbException

from drb.drivers.swift import SwiftAuth, SwiftService
from tests.utility import start_mock_swift, stop_mock_swift, reset_cpt


class TestSwiftObject(unittest.TestCase):
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
        reset_cpt()
        start_mock_swift(cls.storage_url)
        cls.auth = SwiftAuth(preauthurl=cls.storage_url,
                             preauthtoken="token",
                             auth_version=3, os_options=cls._os_options)
        cls.node = SwiftService(auth=cls.auth)
        cls.children = cls.node['container-1']['test.txt']

    @classmethod
    def tearDownClass(cls) -> None:
        stop_mock_swift()

    def test_name(self):
        self.assertEqual('test.txt', self.children.name)

    def test_children(self):
        self.assertIsNotNone(self.children.children)
        self.assertIsInstance(self.children.children, list)
        self.assertEqual(0, len(self.children.children))

    def test_attributes(self):
        self.assertIsNotNone(self.children.attributes)
        self.assertEqual(5, len(self.children.attributes))
        self.assertIsInstance(self.children.attributes, dict)
        swift = {
            ('bytes', None): 19,
            ('content_type', None): 'text/plain',
            ('hash', None): 'cf1ca9285a64cc1cdba842a5d164523e',
            ('last_modified', None): '2022-01-24T10:36:06.598740',
            ('name', None): 'test.txt'
        }
        self.assertEqual(19, self.children.get_attribute("bytes"))
        self.assertEqual(swift, self.children.attributes)
        with self.assertRaises(DrbException):
            self.children.get_attribute("something")
        with self.assertRaises(DrbException):
            self.children.get_attribute("swift", "ns")

    def test_parent(self):
        self.assertEqual(self.node, self.children)
        self.assertEqual(self.node['container-1'], self.children)

    def test_path(self):
        self.assertEqual(
            Path(os.path.sep+'container-1', 'test.txt').as_posix(),
            self.children.path.path)

    def test_impl(self):
        self.assertFalse(self.children.has_impl(DrbNode))
        self.assertTrue(self.children.has_impl(io.BytesIO))
        with self.assertRaises(DrbException):
            self.children.get_impl(DrbNode)
        with self.children.get_impl(io.BytesIO) as stream:
            self.assertEqual('This is my awesome test.',
                             stream.read().decode())
        with self.children.get_impl(io.BytesIO, chunk_size=3) as stream:
            self.assertEqual('This i',
                             stream.read(6).decode())
        with self.children.get_impl(io.BytesIO, chunk_size=1) as stream:
            self.assertEqual('T',
                             stream.read(1).decode())
        # with self.children.get_impl(io.BytesIO,
        #                             temp_url_key='my_secret_key') as stream:
        #     self.assertEqual('This is my awesome test.',
        #                      stream.read().decode())

    def test_has_child(self):
        self.assertFalse(self.children.has_child('test.txt'))
        self.assertFalse(self.children.has_child())
        self.assertFalse(self.children.has_child('container'))
        self.assertFalse(self.children.has_child('test.txt', 'ns'))

    def test_name_space_uri(self):
        self.assertIsNone(self.node.namespace_uri)

    def test_value(self):
        self.assertIsNone(self.node.value)

    def test_auth(self):
        self.assertEqual(self.auth, self.node.get_auth())
