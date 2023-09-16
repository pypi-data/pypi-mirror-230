import unittest

from drb.core import DrbNode
from drb.drivers.http import DrbHttpNode

from drb.drivers.swift import SwiftAuth, SwiftService, SwiftNodeFactory


class TestSwiftFactory(unittest.TestCase):
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
        cls.auth = SwiftAuth(preauthurl=cls.storage_url,
                             preauthtoken="token",
                             auth_version=3, os_options=cls._os_options)
        cls.node = SwiftService(auth=cls.auth)

    def test_create(self):
        factory = SwiftNodeFactory()
        node = factory.create(self.node)
        self.assertIsInstance(node, (SwiftService, DrbNode))

        node = DrbHttpNode(self.storage_url)
        node = factory.create(node)
        self.assertIsInstance(node, (SwiftService, DrbNode))
