# -*- coding: utf-8 -*-
"""Integration tests for blogofile.
"""
import os
import shutil
from tempfile import mkdtemp
try:
    import unittest2 as unittest        # For Python 2.6
except ImportError:
    import unittest                     # flake8 ignore # NOQA
from ... import main


class TestBlogofileInit(unittest.TestCase):
    """Intrgration tests for the blogofile init command.
    """
    def _call_entry_point(self, *args):
        main.main(*args)

    def test_blogofile_init_bare_site(self):
        """blogofile init w/o plugin initializes bare site w/ _config.py file
        """
        src_dir = mkdtemp()
        self.addCleanup(shutil.rmtree, src_dir)
        os.rmdir(src_dir)
        self._call_entry_point(['blogofile', 'init', src_dir])
        self.assertEqual(os.listdir(src_dir), ['_config.py'])
