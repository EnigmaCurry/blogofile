import re
import os
from urlparse import urlparse
import logging

import config

logger = logging.getLogger("blogofile.util")


html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }
    
def html_escape(text): #pragma: no cover
    """Produce entities within text."""
    L=[]
    for c in text:
        L.append(html_escape_table.get(c,c))
    return "".join(L)
    
def should_ignore_path(path):
    """See if a given path matches the ignore patterns"""
    for p in config.compiled_file_ignore_patterns:
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
        raise OSError("a file with the same name as the desired " \
                          "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            mkdir(head)
        #print "mkdir %s" % repr(newdir)
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
    """
    new_parts = []
    for p in parts:
        if hasattr(p,"__iter__"):
            #This part is a sequence itself, recurse into it
            p = path_join(*p, **{'sep':"/"})
        p = p.strip("/")
        if p in ("","\\","/"):
            continue
        new_parts.append(p)
    if len(new_parts) > 0:
        return "/".join(new_parts)
    else:
        return "/"

            
def site_path_helper(*parts):
    """Make an absolute path on the site, appending a sequence of path parts to
    the site path

    >>> config.site_url = "http://www.blogofile.com"
    >>> site_path_helper("blog")
    '/blog'
    >>> config.site_url = "http://www.blgofile.com/~ryan/site1"
    >>> site_path_helper("blog")
    '/~ryan/site1/blog'
    >>> site_path_helper("/blog")
    '/~ryan/site1/blog'
    >>> site_path_helper("blog","/category1")
    '/~ryan/site1/blog/category1'
    """
    site_path = urlparse(config.site_url).path
    path = url_path_helper(site_path,*parts)
    if not path.startswith("/"):
        path = "/" + path
    return path

def fs_site_path_helper(*parts):
    """Build a path relateive to the built site inside the _site dir

    >>> config.site_url = "http://www.blogofile.com/ryan/site1"
    >>> fs_site_path_helper()
    'ryan/site1'
    >>> fs_site_path_helper("/blog","/category","stuff")
    'ryan/site1/blog/category/stuff'
    """
    return site_path_helper(*parts).strip("/")

def path_join(*parts, **kwargs):
    """A better os.path.join

    Converts (back)slashes from other platforms automatically
    Normally, os.path.join is great, as long as you pass each dir/file
    independantly, but not if you (accidentally/intentionally) put a slash in

    if sep is specified, use that as the seperator
    rather than the system default"""
    if kwargs.has_key('sep'):
        sep = kwargs['sep']
    else:
        sep = os.sep
    if os.sep == "\\":
        wrong_slash_type = "/"
    else:
        wrong_slash_type = "\\"
    new_parts = []
    for p in parts:
        if hasattr(p,"__iter__"):
            #This part is a sequence itself, recurse into it
            p = path_join(*p)
        if p in ("","\\","/"):
            continue
        new_parts.append(p.replace(wrong_slash_type,os.sep))
    return sep.join(new_parts)

def recursive_file_list(directory, regex=None):
    "Recursively walk a directory tree and find all the files matching regex"
    if type(regex) == basestring:
        regex = re.compile(regex)
    for root,dirs,files in os.walk(directory):
        for f in files:
            if regex:
                if regex.match(f):
                    yield os.path.join(root,f)
            else:
                yield os.path.join(root,f)

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
    if not isinstance(s, basestring,):
        if hasattr(s, '__unicode__'):
            s = unicode(s)
        else:
            try:
                s = unicode(str(s), encoding, errors)
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
    elif not isinstance(s, unicode):
        # Note: We use .decode() here, instead of unicode(s, encoding,
        # errors), so that if s is a SafeString, it ends up being a
        # SafeUnicode at the end.
        s = s.decode(encoding, errors)
    return s
