import re
import os
import urlparse
import logging

import pygments
import pygments.formatters
import pygments.lexers
import pygments.util

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

def pre_tag_parser(text, occurrence):
    """BeautifulSoup, ElementTree, minidom, they all mess with the insides of
    <pre> tags and it's pissing me off. I guess I'll write my own, hope it's not
    terribly buggy.

    returns a tuple representing Xth (occurrence) pre tag found in text:
    ( pre_tag_contents,
       tag_attrs,
       start_offset,
       end_offset )"""
    current_start_offset = 0
    attr_re = re.compile(r"""([^ ]+)=(?:(?:"([^"]+)")|(?:'([^"]+)')|([^ >]+))""")
    current_occurrence = 0
    while True:
        start_offset = text.find("<pre",current_start_offset)
        end_of_start = text.find(">",start_offset)+1
        end_offset = text.find("</pre",start_offset)
        end_of_end = text.find(">",end_offset)
        if(start_offset==-1 or end_of_start==-1 or end_offset==-1 or end_of_end==-1):
            return None
        current_occurrence += 1
        if current_occurrence < occurrence:
            current_start_offset = end_of_end
            continue
        contents = text[end_of_start:end_offset]
        attrs = {}
        for match in attr_re.findall(text[start_offset:end_of_start]):
            if match[1] != "":
                attrs[match[0]] = match[1]
            elif match[2] != "":
                attrs[match[0]] = match[2]
            elif match[3] != "":
                attrs[match[0]] = match[3]
        return (contents,attrs,start_offset,end_of_end)

def do_syntax_highlight(content,config):
    pre_tag_num = 0
    while True:
        pre_tag_num+=1
        pre_tag_info = pre_tag_parser(content,pre_tag_num)
        if pre_tag_info:
            pre_contents,attrs,start,end = pre_tag_info
            try:
                lexer = pygments.lexers.get_lexer_by_name(attrs['lang'])
            except KeyError, pygments.util.ClassNotFound:
                continue
            h_pre = pygments.highlight(
                pre_contents, lexer,
                config.html_formatter)
            #replace in content:
            content=content[:start]+h_pre+content[end+1:]
        else:
            break
    return content
    
def should_ignore_path(path):
    """See if a given path matches the ignore patterns"""
    for p in config.compiled_ignore_patterns:
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
        new_parts.append(p.replace(wrong_slash_type,os.sep))
    return os.sep.join(new_parts)


