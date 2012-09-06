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

    def test_template_lookup(self):
        """_template_lookup calls mako.lookup.TemplateLookup w/ expected args
        """
        mock_plugin_module = MagicMock(
            config={'name': 'foo'}, __name__='mock_plugin', __file__='./foo')
        with patch.object(plugin, 'TemplateLookup') as mock_TemplateLookup:
            self._make_one(mock_plugin_module)
        mock_TemplateLookup.assert_called_once_with(
            directories=['_templates', './site_src/_templates'],
            input_encoding='utf-8', output_encoding='utf-8',
            encoding_errors='replace')

    def test_get_src_dir(self):
        """get_src_dir method returns expected directory name
        """
        mock_plugin_module = MagicMock(
            config={'name': 'foo'}, __name__='mock_plugin',
            __file__='/foo/bar.py')
        tools = self._make_one(mock_plugin_module)
        src_dir = tools.get_src_dir()
        self.assertEqual(src_dir, '/foo/site_src')

    def test_add_template_dir_append(self):
        """add_template_dir appends to template_lookup.directories by default
        """
        mock_plugin_module = MagicMock(
            config={'name': 'foo'}, __name__='mock_plugin',
            __file__='/foo/bar.py')
        tools = self._make_one(mock_plugin_module)
        tools.add_template_dir('baz')
        self.assertEqual(
            tools.template_lookup.directories,
            ['_templates', '/foo/site_src/_templates', 'baz'])

    def test_add_template_dir_prepend(self):
        """add_template_dir prepends to template_lookup.directories
        """
        mock_plugin_module = MagicMock(
            config={'name': 'foo'}, __name__='mock_plugin',
            __file__='/foo/bar.py')
        tools = self._make_one(mock_plugin_module)
        tools.add_template_dir('baz', append=False)
        self.assertEqual(
            tools.template_lookup.directories,
            ['baz', '_templates', '/foo/site_src/_templates'])

    def test_materialize_template(self):
        """materialize_template calls template.materialize_template w/ exp args
        """
        mock_plugin_module = MagicMock(
            config={'name': 'foo'}, __name__='mock_plugin',
            __file__='/foo/bar.py')
        # nested contexts for Python 2.6 compatibility
        with patch.object(plugin, 'TemplateLookup') as mock_TL:
            tools = self._make_one(mock_plugin_module)
            with patch.object(
                plugin.template, 'materialize_template') as mock_mt:
                tools.materialize_template(
                    'foo.mako', 'bar.html', {'flip': 'flop'})
        mock_mt.assert_called_once_with(
            'foo.mako', 'bar.html', attrs={'flip': 'flop'},
            caller=mock_plugin_module, lookup=mock_TL())

    def test_initialize_controllers(self):
        """initialize_controllers calls controller module init function
        """
        mock_controllers_module_init = MagicMock(name='mock_init')
        mock_controller = MagicMock(
            name='mock_controller',
            mod=MagicMock(
                name='mock_mod',
                init=mock_controllers_module_init))
        mock_plugin_module = MagicMock(
            __name__='mock_plugin', __file__='/foo/bar.py',
            config=MagicMock(
                name='mock_config',
                controllers={'blog': mock_controller}))
        tools = self._make_one(mock_plugin_module)
        tools.initialize_controllers()
        mock_controllers_module_init.assert_called_once_with()

    def test_run_controllers(self):
        """run_controllers calls controller module run function
        """
        mock_controllers_module_run = MagicMock(name='mock_rub')
        mock_controller = MagicMock(
            name='mock_controller',
            mod=MagicMock(
                name='mock_mod',
                run=mock_controllers_module_run))
        mock_plugin_module = MagicMock(
            __name__='mock_plugin', __file__='/foo/bar.py',
            config=MagicMock(
                name='mock_config',
                controllers={'blog': mock_controller}))
        tools = self._make_one(mock_plugin_module)
        tools.run_controllers()
        mock_controllers_module_run.assert_called_once_with()
