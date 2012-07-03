# -*- coding: utf-8 -*-
"""Unit tests for blogofile main module.

Tests entry point function, command line parser, and sub-command
action functions.
"""
import argparse
import logging
import os
import platform
import sys
try:
    import unittest2 as unittest        # For Python 2.6
except ImportError:
    import unittest                     # flake8 ignore # NOQA
from mock import MagicMock
from mock import Mock
from mock import patch
import six
from .. import main


class TestEntryPoint(unittest.TestCase):
    """Unit tests for blogofile entry point function.
    """
    def _call_entry_point(self):
        main.main()

    @patch.object(main, 'setup_command_parser', return_value=(Mock(), []))
    def test_entry_w_too_few_args_prints_help(self, mock_setup_parser):
        """entry with 1 arg calls parser print_help and exits
        """
        mock_parser, mock_subparsers = mock_setup_parser()
        mock_parser.exit = sys.exit
        with patch.object(main, 'sys') as mock_sys:
            mock_sys.argv = ['blogofile']
            with self.assertRaises(SystemExit):
                self._call_entry_point()
        mock_parser.print_help.assert_called_once()

    @patch.object(main, 'setup_command_parser', return_value=(Mock(), []))
    def test_entry_parse_args(self, mock_setup_parser):
        """entry with >1 arg calls parse_args
        """
        mock_parser, mock_subparsers = mock_setup_parser()
        with patch.object(main, 'sys') as mock_sys:
            mock_sys.argv = 'blogofile foo'.split()
            self._call_entry_point()
        mock_parser.parse_args.assert_called_once()

    @patch.object(main, 'setup_command_parser', return_value=(Mock(), []))
    @patch.object(main, 'set_verbosity')
    def test_entry_set_verbosity(self, mock_set_verbosity, mock_setup_parser):
        """entry with >1 arg calls set_verbosity
        """
        mock_parser, mock_subparsers = mock_setup_parser()
        mock_args = Mock()
        mock_parser.parse_args = Mock(return_value=mock_args)
        with patch.object(main, 'sys') as mock_sys:
            mock_sys.argv = 'blogofile foo bar'.split()
            self._call_entry_point()
        mock_set_verbosity.assert_called_once_with(mock_args)

    @patch.object(main, 'setup_command_parser',
                  return_value=(Mock(name='parser'), Mock(name='subparsers')))
    @patch.object(main, 'do_help')
    def test_entry_do_help(self, mock_do_help, mock_setup_parser):
        """entry w/ help in args calls do_help w/ args, parser & subparsers
        """
        mock_parser, mock_subparsers = mock_setup_parser()
        mock_args = Mock(name='args', func=mock_do_help)
        mock_parser.parse_args = Mock(return_value=mock_args)
        with patch.object(main, 'sys') as mock_sys:
            mock_sys.argv = 'blogofile help'.split()
            self._call_entry_point()
        mock_do_help.assert_called_once_with(
            mock_args, mock_parser, mock_subparsers)

    @patch.object(main, 'setup_command_parser', return_value=(Mock(), []))
    def test_entry_arg_func(self, mock_setup_parser):
        """entry with >1 arg calls args.func with args
        """
        mock_parser, mock_subparsers = mock_setup_parser()
        mock_args = Mock()
        mock_parser.parse_args = Mock(return_value=mock_args)
        with patch.object(main, 'sys') as mock_sys:
            mock_sys.argv = 'blogofile foo bar'.split()
            self._call_entry_point()
        mock_args.func.assert_called_once_with(mock_args)


class TestLoggingVerbosity(unittest.TestCase):
    """Unit tests for logging verbosity setup.
    """
    def _call_fut(self, *args):
        """Call the fuction under test.
        """
        main.set_verbosity(*args)

    @patch.object(main, 'logger')
    def test_verbose_mode_sets_INFO_logging(self, mock_logger):
        """verbose==True in args sets INFO level logging
        """
        mock_args = Mock(verbose=True, veryverbose=False)
        self._call_fut(mock_args)
        mock_logger.setLevel.assert_called_once_with(logging.INFO)

    @patch.object(main, 'logger')
    def test_very_verbose_mode_sets_DEBUG_logging(self, mock_logger):
        """veryverbose==True in args sets DEBUG level logging
        """
        mock_args = Mock(verbose=False, veryverbose=True)
        self._call_fut(mock_args)
        mock_logger.setLevel.assert_called_once_with(logging.DEBUG)


class TestParserTemplate(unittest.TestCase):
    """Unit tests for command line parser template.
    """
    def _call_fut(self):
        """Call function under test.
        """
        return main._setup_parser_template()

    @patch('sys.stderr', new_callable=six.StringIO)
    def test_parser_template_version(self, mock_stderr):
        """parser template version arg returns expected string and exits
        """
        from .. import __version__
        parser_template = self._call_fut()
        with self.assertRaises(SystemExit):
            parser_template.parse_args(['--version'])
        self.assertEqual(
            mock_stderr.getvalue(),
            'Blogofile {0} -- http://www.blogofile.com -- {1} {2}\n'
            .format(__version__, platform.python_implementation(),
                    platform.python_version()))

    def test_parser_template_verbose_default(self):
        """parser template sets verbose default to False
        """
        parser_template = self._call_fut()
        args = parser_template.parse_args([])
        self.assertFalse(args.verbose)

    def test_parser_template_verbose_true(self):
        """parser template sets verbose to True when -v in args
        """
        parser_template = self._call_fut()
        args = parser_template.parse_args(['-v'])
        self.assertTrue(args.verbose)

    def test_parser_template_veryverbose_default(self):
        """parser template sets veryverbose default to False
        """
        parser_template = self._call_fut()
        args = parser_template.parse_args([])
        self.assertFalse(args.veryverbose)

    def test_parser_template_veryverbose_true(self):
        """parser template sets veryverbose to True when -vv in args
        """
        parser_template = self._call_fut()
        args = parser_template.parse_args(['-vv'])
        self.assertTrue(args.veryverbose)


class TestHelpParser(unittest.TestCase):
    """Unit tests for help sub-command parser.
    """
    def _parse_args(self, *args):
        """Set up sub-command parser, parse args, and return result.
        """
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        main._setup_help_parser(subparsers)
        return parser.parse_args(*args)

    def test_help_parser_commands_default(self):
        """help w/ no command sets command arg to empty list
        """
        args = self._parse_args(['help'])
        self.assertEqual(args.command, [])

    def test_help_parser_commands(self):
        """help w/ commands sets command arg to list of commands
        """
        args = self._parse_args('help foo bar'.split())
        self.assertEqual(args.command, 'foo bar'.split())

    def test_help_parser_func_do_help(self):
        """help action function is do_help
        """
        args = self._parse_args(['help'])
        self.assertEqual(args.func, main.do_help)


class TestInitParser(unittest.TestCase):
    """Unit tests for init sub-command parser.
    """
    def _parse_args(self, *args):
        """Set up sub-command parser, parse args, and return result.
        """
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        main._setup_init_parser(subparsers)
        return parser.parse_args(*args)

    def test_init_parser_src_dir_arg(self):
        """init parser sets src_dir arg to given arg
        """
        args = self._parse_args('init foo'.split())
        self.assertEqual(args.src_dir, 'foo')

    def test_init_parser_plugin_default(self):
        """init parser sets default plugin arg to None
        """
        args = self._parse_args('init foo'.split())
        self.assertEqual(args.plugin, None)

    def test_init_parser_plugin_arg(self):
        """init parser sets plugin arg to given arg
        """
        args = self._parse_args('init foo bar'.split())
        self.assertEqual(args.plugin, 'bar')

    def test_init_parser_func_do_build(self):
        """init action function is do_init
        """
        args = self._parse_args('init foo'.split())
        self.assertEqual(args.func, main.do_init)


class TestDoInit(unittest.TestCase):
    """Unit tests for init sub-command action function.
    """
    def _call_fut(self, args):
        """Call the fuction under test.
        """
        main.do_init(args)

    @patch.object(main.os.path, 'exists', return_value=True)
    @patch('sys.stderr', new_callable=six.StringIO)
    def test_do_init_not_overwrite_existing_src_dir(self, mock_stderr,
                                                    mock_path_exists):
        """do_init won't overwrite existing src_dir and exits w/ msg
        """
        args = Mock(src_dir='foo/bar', plugin=None)
        with self.assertRaises(SystemExit):
            self._call_fut(args)
        self.assertEqual(
            mock_stderr.getvalue(),
            '{0.src_dir} already exists; initialization aborted\n'
            .format(args))

    @patch.object(main.os.path, 'exists', return_value=False)
    @patch.object(main, '_init_bare_site', autospec=True)
    def test_do_init_wo_plugin_calls_init_bare_site(self, mock_init_bare_site,
                                                    mock_path_exists):
        """do_init w/o plugin calls _init_bare_site w/ src_dir arg
        """
        args = Mock(src_dir='foo/bar', plugin=None)
        self._call_fut(args)
        mock_init_bare_site.assert_called_once_with(args.src_dir)

    @patch.object(main.os.path, 'exists', return_value=False)
    @patch.object(main, '_init_plugin_site', autospec=True)
    def test_do_init_w_plugin_init_plugin_site(self, mock_init_plugin_site,
                                               mock_path_exists):
        """do_init w plugin calls _init_plugin_site w/ args
        """
        args = Mock(src_dir='foo/bar', plugin='blog')
        self._call_fut(args)
        mock_init_plugin_site.assert_called_once_with(args)


class TestInitBareSite(unittest.TestCase):
    """Unit tests _init_bare_site function.
    """
    def _call_fut(self, args):
        """Call the fuction under test.
        """
        main._init_bare_site(args)

    @patch.object(main.os, 'makedirs', autospec=True)
    def test_init_bare_site_creates_src_dir(self, mock_mkdirs):
        """_init_bare_site calls os.makedirs to create src_dir c/w parents
        """
        src_dir = 'foo/bar'
        with patch.object(main, 'open', create=True) as mock_open:
            spec = six.StringIO if six.PY3 else file
            mock_open.return_value = MagicMock(spec=spec)
            self._call_fut(src_dir)
        mock_mkdirs.assert_called_once_with(src_dir)

    @patch.object(main.os, 'makedirs')
    def test_init_bare_site_writes_to_config_file(self, mock_mkdirs):
        """_init_bare_site writes new _config.py file
        """
        with patch.object(main, 'open', create=True) as mock_open:
            spec = six.StringIO if six.PY3 else file
            mock_open.return_value = MagicMock(spec=spec)
            new_config_handle = mock_open.return_value.__enter__.return_value
            self._call_fut('foo/bar')
            self.assertTrue(new_config_handle.writelines.called)

    @patch.object(main.os, 'makedirs')
    def test_init_bare_site_writes_config(self, mock_mkdirs):
        """_init_bare_site writes expected lines to new _config.py file
        """
        with patch.object(main, 'open', create=True) as mock_open:
            spec = six.StringIO if six.PY3 else file
            mock_open.return_value = MagicMock(spec=spec)
            new_config_handle = mock_open.return_value.__enter__.return_value
            self._call_fut('foo/bar')
            new_config_handle.writelines.called_with('# -*- coding: utf-8 -*-')

    @patch.object(main.os, 'makedirs')
    @patch('sys.stdout', new_callable=six.StringIO)
    def test_init_bare_site_prints_config_written_msg(self, mock_stdout,
                                                      mock_mkdirs):
        """_init_bare_site prints msg re: creation of _config.py file
        """
        src_dir = 'foo/bar'
        with patch.object(main, 'open', create=True) as mock_open:
            spec = six.StringIO if six.PY3 else file
            mock_open.return_value = MagicMock(spec=spec)
            self._call_fut(src_dir)
        self.assertEqual(
            mock_stdout.getvalue(),
            '_config.py for a bare (do-it-yourself) site written to {0}\n'
            'If you were expecting more, please see `blogofile init -h`\n'
            .format(src_dir))


class TestInitPluginSite(unittest.TestCase):
    """Unit tests _init_plugin_site function.
    """
    def _call_fut(self, *args):
        """Call the fuction under test.
        """
        main._init_plugin_site(*args)

    @patch.object(main.shutil, 'copytree')
    def test_init_plugin_site_gets_plugin_by_name(self, mock_copytree):
        """_init_plugin_site calls plugin.get_by_name w/ plugin arg
        """
        from .. import plugin as plugin_module
        args = Mock(src_dir='foo/bar', plugin='baz')
        mock_plugin = Mock(__file__='baz_plugin/__init__.py')
        patch_get_by_name = patch.object(
            plugin_module, 'get_by_name', return_value=mock_plugin)
        with patch_get_by_name as mock_get_by_name:
            self._call_fut(args)
        mock_get_by_name.assert_called_once_with(args.plugin)

    @patch('sys.stderr', new_callable=six.StringIO)
    def test_init_plugin_site_msg_re_unknown_plugin(self, mock_stderr):
        """_init_plugin_site shows msg if plugin arg not found
        """
        from .. import plugin as plugin_module
        args = Mock(src_dir='foo/bar', plugin='baz')
        patch_get_by_name = patch.object(
            plugin_module, 'get_by_name', return_value=None)
        patch_open = patch.object(main, 'open', create=True)
        # nested contexts for Python 2.6 compatibility
        with patch_open as mock_open:
            spec = six.StringIO if six.PY3 else file
            mock_open.return_value = MagicMock(spec=spec)
            with patch_get_by_name:
                self._call_fut(args)
        self.assertTrue(
            mock_stderr.getvalue().startswith(
                '{0.plugin} plugin not installed; initialization aborted\n\n'
                'installed plugins:\n'.format(args)))

    @patch('sys.stderr', new_callable=six.StringIO)
    def test_init_plugin_site_plugin_list_if_unknown_plugin(self, mock_stderr):
        """
        """
        from .. import plugin as plugin_module
        args = Mock(src_dir='foo/bar', plugin='baz')
        patch_get_by_name = patch.object(
            plugin_module, 'get_by_name', return_value=None)
        patch_list_plugins = patch.object(plugin_module, 'list_plugins')
        patch_open = patch.object(main, 'open', create=True)
        # nested contexts for Python 2.6 compatibility
        with patch_list_plugins as mock_list_plugins:
            with patch_get_by_name:
                with patch_open:
                    self._call_fut(args)
        assert mock_list_plugins.called

    @patch.object(main.shutil, 'copytree')
    @patch.object(main.shutil, 'ignore_patterns')
    def test_init_plugin_site_ignore_dirs(self, mock_ignore_patterns,
                                          mock_copytree):
        """_init_plugin_site calls shutil.ignore_patterns w/ expected dirs
        """
        from .. import plugin as plugin_module
        args = Mock(src_dir='foo/bar', plugin='baz')
        mock_plugin = Mock(__file__='baz_plugin/__init__.py')
        patch_get_by_name = patch.object(
            plugin_module, 'get_by_name', return_value=mock_plugin)
        with patch_get_by_name:
            self._call_fut(args)
        mock_ignore_patterns.assert_called_once_with(
            '_controllers', '_filters')

    @patch.object(main.shutil, 'ignore_patterns')
    @patch.object(main.shutil, 'copytree')
    def test_init_plugin_site_copies_site_src_tree(self, mock_copytree,
                                                   mock_ignore_patterns):
        """_init_plugin_site calls shutil.copytree w/ expected args
        """
        from .. import plugin as plugin_module
        args = Mock(src_dir='foo/bar', plugin='baz')
        mock_plugin = Mock(__file__='baz_plugin/__init__.py')
        patch_get_by_name = patch.object(
            plugin_module, 'get_by_name', return_value=mock_plugin)
        with patch_get_by_name:
            self._call_fut(args)
            mock_plugin_path = os.path.dirname(
                os.path.realpath(mock_plugin.__file__))
            mock_site_src = os.path.join(mock_plugin_path, 'site_src')
        mock_copytree.assert_called_once_with(
            mock_site_src, args.src_dir, ignore=mock_ignore_patterns())

    @patch.object(main.shutil, 'copytree')
    @patch('sys.stdout', new_callable=six.StringIO)
    def test_init_plugin_site_prints_config_written_msg(self, mock_stdout,
                                                        mock_copytree):
        """_init_plugin_site prints msg re: creation of _config.py file
        """
        from .. import plugin as plugin_module
        args = Mock(src_dir='foo/bar', plugin='baz')
        mock_plugin = Mock(__file__='baz_plugin/__init__.py')
        patch_get_by_name = patch.object(
            plugin_module, 'get_by_name', return_value=mock_plugin)
        patch_open = patch.object(main, 'open', create=True)
        # nested contexts for Python 2.6 compatibility
        with patch_open as mock_open:
            spec = six.StringIO if six.PY3 else file
            mock_open.return_value = MagicMock(spec=spec)
            with patch_get_by_name:
                self._call_fut(args)
        self.assertEqual(
            mock_stdout.getvalue(),
            '{0.plugin} plugin site_src files written to {0.src_dir}\n'
            .format(args))


class TestBuildParser(unittest.TestCase):
    """Unit tests for build sub-command parser.
    """
    def _parse_args(self, *args):
        """Set up sub-command parser, parse args, and return result.
        """
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        main._setup_build_parser(subparsers)
        return parser.parse_args(*args)

    def test_build_parser_src_dir_default(self):
        """build parser sets src_dir default to relative cwd
        """
        args = self._parse_args(['build'])
        self.assertEqual(args.src_dir, '.')

    def test_build_parser_src_dir_value(self):
        """build parser sets src_dir to arg value
        """
        args = self._parse_args('build -s foo'.split())
        self.assertEqual(args.src_dir, 'foo')

    def test_build_parser_func_do_build(self):
        """build action function is do_build
        """
        args = self._parse_args(['build'])
        self.assertEqual(args.func, main.do_build)


class TestServeParser(unittest.TestCase):
    """Unit tests for serve sub-command parser.
    """
    def _parse_args(self, *args):
        """Set up sub-command parser, parse args, and return result.
        """
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        main._setup_serve_parser(subparsers)
        return parser.parse_args(*args)

    def test_serve_parser_ip_addr_default(self):
        """serve parser sets ip address default to 127.0.0.1
        """
        args = self._parse_args(['serve'])
        self.assertEqual(args.IP_ADDR, '127.0.0.1')

    def test_serve_parser_ip_addr_arg(self):
        """serve parser sets ip address to given arg
        """
        args = self._parse_args('serve 8888 192.168.1.5'.split())
        self.assertEqual(args.IP_ADDR, '192.168.1.5')

    def test_serve_parser_port_default(self):
        """serve parser sets ip address default to 127.0.0.1
        """
        args = self._parse_args(['serve'])
        self.assertEqual(args.PORT, '8080')

    def test_serve_parser_port_arg(self):
        """serve parser sets port to given arg
        """
        args = self._parse_args('serve 8888'.split())
        self.assertEqual(args.PORT, '8888')

    def test_serve_parser_src_dir_default(self):
        """serve parser sets src_dir default to relative cwd
        """
        args = self._parse_args(['serve'])
        self.assertEqual(args.src_dir, '.')

    def test_serve_parser_src_dir_value(self):
        """serve parser sets src_dir to arg value
        """
        args = self._parse_args('serve -s foo'.split())
        self.assertEqual(args.src_dir, 'foo')

    def test_serve_parser_func_do_serve(self):
        """serve action function is do_serve
        """
        args = self._parse_args(['serve'])
        self.assertEqual(args.func, main.do_serve)


class TestInfoParser(unittest.TestCase):
    """Unit tests for info sub-command parser.
    """
    def _parse_args(self, *args):
        """Set up sub-command parser, parse args, and return result.
        """
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        main._setup_info_parser(subparsers)
        return parser.parse_args(*args)

    def test_info_parser_src_dir_default(self):
        """info parser sets src_dir default to relative cwd
        """
        args = self._parse_args(['info'])
        self.assertEqual(args.src_dir, '.')

    def test_info_parser_src_dir_value(self):
        """info parser sets src_dir to arg value
        """
        args = self._parse_args('info -s foo'.split())
        self.assertEqual(args.src_dir, 'foo')

    def test_info_parser_func_do_info(self):
        """info action function is do_info
        """
        args = self._parse_args(['info'])
        self.assertEqual(args.func, main.do_info)


class TestPluginsParser(unittest.TestCase):
    """Unit tests for plugins sub-command parser.
    """
    def _parse_args(self, *args):
        """Set up sub-command parser, parse args, and return result.
        """
        parser_template = argparse.ArgumentParser(add_help=False)
        parser = argparse.ArgumentParser(parents=[parser_template])
        subparsers = parser.add_subparsers()
        main._setup_plugins_parser(subparsers, parser_template)
        return parser.parse_args(*args)

    def test_plugins_parser_func_list_plugins(self):
        """plugins list action function is plugin.list_plugins
        """
        args = self._parse_args('plugins list'.split())
        self.assertEqual(args.func, main.plugin.list_plugins)


class TestFiltersParser(unittest.TestCase):
    """Unit tests for filters sub-command parser.
    """
    def _parse_args(self, *args):
        """Set up sub-command parser, parse args, and return result.
        """
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        main._setup_filters_parser(subparsers)
        return parser.parse_args(*args)

    def test_filters_parser_func_list_filters(self):
        """filters list action function is _filter.list_filters
        """
        args = self._parse_args('filters list'.split())
        self.assertEqual(args.func, main._filter.list_filters)
