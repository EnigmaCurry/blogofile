# -*- coding: utf-8 -*-
"""Unit tests for blogofile plugin module.
"""
try:
    import unittest2 as unittest        # For Python 2.6
except ImportError:
    import unittest                     # flake8 ignore # NOQA
from mock import Mock
from mock import patch
from .. import plugin


class TestGetByName(unittest.TestCase):
    """Unit tests for get_by_name function.
    """
    def _call_fut(self, *args):
        """Call the fuction under test.
        """
        return plugin.get_by_name(*args)

    def test_get_by_name(self):
        """get_by_name returns plugin with matching name
        """
        mock_plugin = Mock(__dist__={'config_name': 'foo'})
        with patch.object(plugin, 'iter_plugins', return_value=[mock_plugin]):
            p = self._call_fut('foo')
        self.assertEqual(p, mock_plugin)
