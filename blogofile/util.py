import re
import os
import urlparse
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
    
def html_escape(text):
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
            
def blog_path_helper(path_parts):
    """Make an absolute URL path for something on the blog"""
    if type(path_parts) in (str, unicode):
        path_parts = (path_parts,)
    a_path = urlparse.urlsplit(config.site_url).path
    a_path = "/".join((a_path,config.blog_path))
    a_path = a_path + "/" + "/".join(path_parts)
    if not a_path.startswith("/"):
        a_path = "/"+a_path
    return a_path

def path_join(*parts):
    """An OS independant os.path.join

    Converts (back)slashes from other platforms automatically
    Normally, os.path.join is great, as long as you pass each dir/file
    independantly, but not if you (accidentally/intentionally) put a slash in"""

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
    return os.sep.join(new_parts)


