# -*- coding: utf-8 -*-
"""Unit tests for blogofile plugin module.
"""
try:
    import unittest2 as unittest        # For Python 2.6
except ImportError:
    import unittest                     # flake8 ignore # NOQA
from mock import (
    MagicMock,
    patch,
)
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
        mock_plugin = MagicMock(__dist__={'config_name': 'foo'})
        with patch.object(plugin, 'iter_plugins', return_value=[mock_plugin]):
            p = self._call_fut('foo')
        self.assertEqual(p, mock_plugin)


class TestPluginTools(unittest.TestCase):
    """Unit tests for PluginTools class.
    """
    def _get_target_class(self):
        from ..plugin import PluginTools
        return PluginTools

    def _make_one(self, *args):
        return self._get_target_class()(*args)

    def test_init_module_attribute(self):
        """PluginTools instance has module attribute
        """
        mock_plugin_module = MagicMock(
            config={'name': 'foo'}, __name__='mock_plugin', __file__='./foo')
        tools = self._make_one(mock_plugin_module)
        self.assertEqual(tools.module, mock_plugin_module)

    def test_init_namespace_attribute(self):
        """PluginTools instance namespace attr is plugin module config var
        """
        mock_plugin_module = MagicMock(
            config={'name': 'foo'}, __name__='mock_plugin', __file__='./foo')
        tools = self._make_one(mock_plugin_module)
        self.assertEqual(tools.namespace, mock_plugin_module.config)

    def test_init_template_lookup_attribute(self):
        """PluginTools template_lookup attr is mako.lookup.TemplateLookup
        """
        from mako.lookup import TemplateLookup
        mock_plugin_module = MagicMock(
            config={'name': 'foo'}, __name__='mock_plugin', __file__='./foo')
        tools = self._make_one(mock_plugin_module)
        self.assertIsInstance(tools.template_lookup, TemplateLookup)

    def test_init_logger_name(self):
        """PluginTools logger has plugin name
        """
        mock_plugin_module = MagicMock(
            config={'name': 'foo'}, __name__='mock_plugin', __file__='./foo')
        tools = self._make_one(mock_plugin_module)
        self.assertEqual(
            tools.logger.name,
            'blogofile.plugins.{0}'.format(mock_plugin_module.__name__))
