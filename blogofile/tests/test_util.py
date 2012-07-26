# -*- coding: utf-8 -*-
"""Unit tests for blogofile util module.
"""
try:
    import unittest2 as unittest        # For Python 2.6
except ImportError:
    import unittest                     # flake8 ignore # NOQA
from mock import (
    MagicMock,
    patch,
    )
import six
from .. import util


@patch.object(util.bf, 'config')
class TestCreateSlug(unittest.TestCase):
    """Unit tests for create_slug function.
    """
    def _call_fut(self, *args):
        """Call the fuction under test.
        """
        return util.create_slug(*args)

    def test_create_slug_ascii(self, mock_config):
        """create_slug returns expected result for ASCII title
        """
        mock_config.site = MagicMock(slugify=None, slug_unicode=None)
        mock_config.blog = MagicMock(slugify=None)
        slug = self._call_fut('Foo Bar!')
        self.assertEqual(slug, 'foo-bar')

    def test_create_slug_unidecode(self, mock_config):
        """create_slug returns expected ASCII result for Unicode title
        """
        mock_config.site = MagicMock(slugify=None, slug_unicode=None)
        mock_config.blog = MagicMock(slugify=None)
        slug = self._call_fut(six.u('\u5317\u4EB0'))
        self.assertEqual(slug, 'bei-jing')

    def test_create_slug_unicode(self, mock_config):
        """create_slug returns expected Unicode result for Unicode title
        """
        mock_config.site = MagicMock(slugify=None, slug_unicode=True)
        mock_config.blog.slugify = None
        slug = self._call_fut(six.u('\u5317\u4EB0'))
        self.assertEqual(slug, six.u('\u5317\u4EB0'))

    def test_create_slug_user_site_slugify(self, mock_config):
        """create_slug uses user-defined config.site.slugify function
        """
        mock_config.site = MagicMock(slugify=lambda s: 'bar-foo')
        mock_config.blog = MagicMock(slugify=None)
        slug = self._call_fut('Foo Bar!')
        self.assertEqual(slug, 'bar-foo')

    def test_create_slug_user_blog_slugify(self, mock_config):
        """create_slug uses user-defined config.blog.slugify function
        """
        mock_config.site = MagicMock(slugify=None)
        mock_config.blog = MagicMock(slugify=lambda s: 'deprecated')
        slug = self._call_fut('Foo Bar!')
        self.assertEqual(slug, 'deprecated')
