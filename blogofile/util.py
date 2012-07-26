# -*- coding: utf-8 -*-
"""Blogofile utility functions.
"""
from __future__ import print_function
import re
import os
import sys
import logging
import fileinput
try:
    from urllib.parse import urlparse   # For Python 2
except ImportError:
    from urlparse import urlparse       # For Python 3; flake8 ignore # NOQA
from markupsafe import Markup
import six
from unidecode import unidecode
from .cache import bf
bf.util = sys.modules['blogofile.util']


logger = logging.getLogger("blogofile.util")

# Word separators and punctuation for slug creation
PUNCT_RE = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }


def html_escape(text):
    """Produce entities within text.
    """
    L = []
    for c in text:
        L.append(html_escape_table.get(c, c))
    return "".join(L)


def should_ignore_path(path):
    """See if a given path matches the ignore patterns.
    """
    if os.path.sep == '\\':
        path = path.replace('\\', '/')
    for p in bf.config.site.compiled_file_ignore_patterns:
        if p.match(path):
            return True
    return False


def mkdir(newdir):
    """works the way a good mkdir should :)
    - already exists, silently complete
    - regular file in the way, raise an exception
    - parent directory(ies) does not exist, make them as well
    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired "
                      "dir, '{0}', already exists.".format(newdir))
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            mkdir(head)
        # print "mkdir {0}.format(repr(newdir))
        if tail:
            os.mkdir(newdir)


def url_path_helper(*parts):
    """
    path_parts is a sequence of path parts to concatenate

    >>> url_path_helper("one","two","three")
    'one/two/three'
    >>> url_path_helper(("one","two"),"three")
    'one/two/three'
    >>> url_path_helper("one/two","three")
    'one/two/three'
    >>> url_path_helper("one","/two/","three")
    'one/two/three'
    >>> url_path_helper("/one","two","three")
    'one/two/three'
    """
    new_parts = []
    for p in parts:
        if hasattr(p, "__iter__") and not isinstance(p, str):
            # This part is a sequence itself, recurse into it
            p = path_join(*p, **{'sep': "/"})
        p = p.strip("/")
        if p in ("", "\\", "/"):
            continue
        new_parts.append(p)

    if len(new_parts) > 0:
        return "/".join(new_parts)
    else:
        return "/"


def site_path_helper(*parts):
    """Make an absolute path on the site, appending a sequence of path parts to
    the site path.

    >>> bf.config.site.url = "http://www.blogofile.com"
    >>> site_path_helper("blog")
    '/blog'
    >>> bf.config.site.url = "http://www.blgofile.com/~ryan/site1"
    >>> site_path_helper("blog")
    '/~ryan/site1/blog'
    >>> site_path_helper("/blog")
    '/~ryan/site1/blog'
    >>> site_path_helper("blog","/category1")
    '/~ryan/site1/blog/category1'
    """
    site_path = urlparse(bf.config.site.url).path
    path = url_path_helper(site_path, *parts)
    if not path.startswith("/"):
        path = "/" + path
    return path


def fs_site_path_helper(*parts):
    """Build a path relative to the built site inside the _site dir.

    >>> bf.config.site.url = "http://www.blogofile.com/ryan/site1"
    >>> fs_site_path_helper()
    ''
    >>> fs_site_path_helper("/blog","/category","stuff")
    'blog/category/stuff'
    """
    return path_join(url_path_helper(*parts).strip("/"))


#TODO: seems to have a lot in common with url_path_helper; commonize
def path_join(*parts, **kwargs):
    """A better os.path.join.

    Converts (back)slashes from other platforms automatically
    Normally, os.path.join is great, as long as you pass each dir/file
    independantly, but not if you (accidentally/intentionally) put a slash in

    If sep is specified, use that as the seperator rather than the
    system default.
    """
    if 'sep' in kwargs:
        sep = kwargs['sep']
    else:
        sep = os.sep
    if os.sep == "\\":
        wrong_slash_type = "/"
    else:
        wrong_slash_type = "\\"
    new_parts = []
    for p in parts:
        if hasattr(p, "__iter__") and not isinstance(p, str):
            #This part is a sequence itself, recurse into it
            p = path_join(*p)
        if p in ("", "\\", "/"):
            continue
        new_parts.append(p.replace(wrong_slash_type, os.sep))
    return sep.join(new_parts)


def recursive_file_list(directory, regex=None):
    """Recursively walk a directory tree and find all the files matching regex.
    """
    if type(regex) == str:
        regex = re.compile(regex)
    for root, dirs, files in os.walk(directory):
        for f in files:
            if regex:
                if regex.match(f):
                    yield os.path.join(root, f)
            else:
                yield os.path.join(root, f)


def rewrite_strings_in_files(existing_string, replacement_string, paths):
    """Replace existing_string with replacement_string
    in all the files listed in paths"""
    for line in fileinput.input(paths, inplace=True):
        #inplace=True redirects sys.stdout back to the file
        line = line.replace(existing_string, replacement_string)
        sys.stdout.write(line)


def force_unicode(s, encoding='utf-8', strings_only=False, errors='strict'):  #pragma: no cover
    """
    Force a string to be unicode.

    If strings_only is True, don't convert (some) non-string-like objects.

    Originally copied from the Django source code, further modifications have
    been made.

    Original copyright and license:

        Copyright (c) Django Software Foundation and individual contributors.
        All rights reserved.

        Redistribution and use in source and binary forms, with or without modification,
        are permitted provided that the following conditions are met:

            1. Redistributions of source code must retain the above copyright notice,
               this list of conditions and the following disclaimer.

            2. Redistributions in binary form must reproduce the above copyright
               notice, this list of conditions and the following disclaimer in the
               documentation and/or other materials provided with the distribution.

            3. Neither the name of Django nor the names of its contributors may be used
               to endorse or promote products derived from this software without
               specific prior written permission.

        THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
        ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
        WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
        DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
        ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
        (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
        LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
        ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
        (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
        SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
    """
    if strings_only and is_protected_type(s):
        return s
    if not isinstance(s, str,):
        if hasattr(s, '__unicode__'):
            s = str(s)
        else:
            try:
                s = str(str(s), encoding, errors)
            except UnicodeEncodeError:
                if not isinstance(s, Exception):
                    raise
                # If we get to here, the caller has passed in an Exception
                # subclass populated with non-ASCII data without special
                # handling to display as a string. We need to handle this
                # without raising a further exception. We do an
                # approximation to what the Exception's standard str()
                # output should be.
                s = ' '.join([force_unicode(arg, encoding, strings_only,
                        errors) for arg in s])
    elif not isinstance(s, str):
        # Note: We use .decode() here, instead of unicode(s, encoding,
        # errors), so that if s is a SafeString, it ends up being a
        # SafeUnicode at the end.
        s = s.decode(encoding, errors)
    return s


def create_slug(title, delim='-'):
    """Create a slug from `title`, with words lowercased, and
    separated by `delim`.

    User may provide their own function to do this via `config.site.slugify`.

    `config.site.slug_unicode` controls whether Unicode characters are included
    in the slug as is, or mapped to reasonable ASCII equivalents.
    """
    # Dispatch to user-supplied slug creation function, if one exists
    if bf.config.site.slugify:
        return bf.config.site.slugify(title)
    elif bf.config.blog.slugify:
        # For backward compatibility
        return bf.config.blog.slugify(title)
    # Get rid of any HTML entities
    slug = Markup(title).unescape()
    result = []
    for word in PUNCT_RE.split(slug):
        if not bf.config.site.slug_unicode:
            result.extend(unidecode(word).split())
        else:
            result.append(word)
    slug = six.text_type(delim.join(result)).lower()
    return slug
