# -*- coding: utf-8 -*-
"""Unit tests for blogofile command line parser.
"""
import logging
import platform
import sys
try:
    import unittest2 as unittest        # For Python 2.6
except ImportError:
    import unittest                     # NOQA
from mock import Mock
from mock import patch
from six.moves import cStringIO as StringIO
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
            self.assertRaises(SystemExit, self._call_entry_point)
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
        return main._build_parser_template()

    def test_parser_template_src_dir_default(self):
        """parser template sets src_dir default to relative cwd
        """
        parser_template = self._call_fut()
        args = parser_template.parse_args([])
        self.assertEqual(args.src_dir, '.')

    def test_parser_template_src_dir_value(self):
        """parser template sets src_dir to arg value
        """
        parser_template = self._call_fut()
        args = parser_template.parse_args('-s foo'.split())
        self.assertEqual(args.src_dir, 'foo')

    @patch('sys.stderr', new_callable=StringIO)
    def test_parser_template_version(self, mock_stderr):
        """parser template version arg returns expected string and exits
        """
        from .. import __version__
        parser_template = self._call_fut()
        self.assertRaises(
            SystemExit, parser_template.parse_args, ['--version'])
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
