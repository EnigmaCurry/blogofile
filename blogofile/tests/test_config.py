# -*- coding: utf-8 -*-
"""Unit tests for blogofile config module.
"""
import os
try:
    import unittest2 as unittest        # For Python 2.6
except ImportError:
    import unittest                     # flake8 ignore # NOQA
from mock import (
    MagicMock,
    mock_open,
    patch,
    )
from .. import config


class TestConfigModuleAttributes(unittest.TestCase):
    """Unit tests for attributes that config exposes in its module scope.
    """
    def test_bf_config_is_module(self):
        """config has bf.config attribute that is a module
        """
        from types import ModuleType
        self.assertIsInstance(config.bf.config, ModuleType)

    def test_bf_config_module_name(self):
        """bf.config attribute is blogofile.config module
        """
        self.assertEqual(config.bf.config.__name__, 'blogofile.config')

    def test_site_is_hierarchical_cache(self):
        """config has site attribute that is a HierarchicalCache object
        """
        from ..cache import HierarchicalCache
        self.assertIsInstance(config.site, HierarchicalCache)

    def test_controllers_is_hierarchical_cache(self):
        """config has controllers attribute that is a HierarchicalCache object
        """
        from ..cache import HierarchicalCache
        self.assertIsInstance(config.controllers, HierarchicalCache)

    def test_filters_is_hierarchical_cache(self):
        """config has filters attribute that is a HierarchicalCache object
        """
        from ..cache import HierarchicalCache
        self.assertIsInstance(config.filters, HierarchicalCache)

    def test_plugins_is_hierarchical_cache(self):
        """config has plugins attribute that is a HierarchicalCache object
        """
        from ..cache import HierarchicalCache
        self.assertIsInstance(config.plugins, HierarchicalCache)

    def test_templates_is_hierarchical_cache(self):
        """config has templates attribute that is a HierarchicalCache object
        """
        from ..cache import HierarchicalCache
        self.assertIsInstance(config.templates, HierarchicalCache)

    def test_default_config_path(self):
        """config has default_config_path attr set to default_config module
        """
        self.assertEqual(
            config.default_config_path,
            os.path.join(os.path.abspath('blogofile'), 'default_config.py'))


class TestConfigInitInteractive(unittest.TestCase):
    """Unit tests for init_interactive function.
    """
    def _call_fut(self, *args):
        """Call the function under test.
        """
        return config.init_interactive(*args)

    def test_init_interactive_loads_user_config(self):
        """init_interactive loads value from user _config.py
        """
        args = MagicMock(src_dir='foo')
        mo = mock_open(read_data='site.url = "http://www.example.com/test/"')
        with patch.object(config, 'open', mo, create=True):
            self._call_fut(args)
        self.assertEqual(config.site.url, 'http://www.example.com/test/')

    def test_init_interactive_no_config_raises_SystemExit(self):
        """init_interactive raises SystemExit when no _config.py exists
        """
        args = MagicMock(src_dir='foo')
        with self.assertRaises(SystemExit):
            self._call_fut(args)


class TestConfigLoadConfig(unittest.TestCase):
    """Unit tests for _load_config function.
    """
    def _call_fut(self, *args):
        """Call the function under test.
        """
        return config._load_config(*args)

    def test_init_interactive_loads_default_config(self):
        """init_interactive loads values from default_config.py
        """
        with patch.object(config, 'open', mock_open(), create=True):
            self._call_fut('_config.py')
        self.assertEqual(config.site.url, 'http://www.example.com')

    def test_load_config_no_config_raises_IOError(self):
        """_load_config raises IOError when no _config.py exists
        """
        with self.assertRaises(IOError):
            self._call_fut('_config.py')
