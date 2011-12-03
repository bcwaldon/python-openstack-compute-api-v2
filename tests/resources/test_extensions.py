
import unittest

from openstack.compute.api.v2.resources import extensions
from tests import fakes


cs = fakes.FakeClient()


class ExtensionsTest(unittest.TestCase):

    def test_list_extensions(self):
        objs = cs.extensions.list()
        cs.assert_called('GET', '/extensions')
        [self.assertTrue(isinstance(obj, extensions.Extension)) for obj in objs]

    def test_get_extensions_details(self):
        obj = cs.extensions.get('os-blargh')
        cs.assert_called('GET', '/extensions/os-blargh')
        self.assertTrue(isinstance(obj, extensions.Extension))
        self.assertEqual(obj.alias, 'os-blargh')
        self.assertEqual(obj.name, 'Blargh Extension')
