#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
post.py parses post sources from the ./_post directory.
"""

__author__ = "Ryan McGuire (ryan@enigmacurry.com)"
__date__   = "Mon Feb  2 21:21:04 2009"

import os
import datetime
import re
import operator
import urlparse

import pytz
import yaml
import textile
import markdown

date_format = "%Y/%m/%d %H:%M:%S"

class PostFormatException(Exception):
    pass

class Post:
    """
    Class to describe a blog post and associated metadata
    
    A simple post:
    
    >>> src = '''
    ... ---
    ... title: First Post
    ... date: 2008/10/20
    ... categories: Cool Stuff , Emacs, Python,   other stuff
    ... permalink: /2008/10/20/first-post
    ... ---
    ... 
    ... This is a test.
    ... '''
    >>> p = Post(src)
    >>> p.title
    u'First Post'
    >>> p.date
    datetime.datetime(2008, 10, 20, 0, 0)
    >>> p.categories == set([u'Cool Stuff',u'Emacs',u'Python',u'other stuff'])
    True
    >>> p.permalink
    u'/2008/10/20/first-post'
    """
    def __init__(self, source, timezone):
        self.source     = source
        self.yaml       = yaml
        self.title      = u"Untitled - " + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        self.date       = datetime.datetime.now(pytz.timezone(timezone))
        self.__timezone = timezone
        self.updated    = self.date
        self.categories = set([u'Uncategorized'])
        self.tags       = set()
        self.permalink  = None
        self.content    = u""
        self.format     = "html"
        self.author     = ""
        self.guid       = None #Default guid is permalink
        self.draft      = False
        self.__parse()
        
    def __repr__(self):
        return "<Post title='%s' date='%s'>" % \
            (self.title, self.date.strftime("%Y/%m/%d %H:%M:%S"))
        
    def __parse(self):
        """Parse the yaml and fill fields"""
        yaml_sep = re.compile("^---$", re.MULTILINE)
        content_parts = yaml_sep.split(self.source, maxsplit=2)
        if len(content_parts) < 2:
            #No yaml to extract
            post_src = self.content
        else:
            #Extract the yaml at the top
            self.__parse_yaml(content_parts[1])
            post_src = content_parts[2]
        #Convert post to HTML
        if self.format == "textile":
            self.content = textile.textile(post_src).decode("utf-8")
        elif self.format == "markdown":
            self.content = markdown.markdown(post_src).decode("utf-8")
        elif self.format == "html":
            self.content = post_src.decode("utf-8")
        else:
            raise PostFormatException("Post format '%s' not recognized." % self.format)
        
    def __parse_yaml(self, yaml_src):
        y = yaml.load(yaml_src)
        try:
            self.title = y['title']
        except KeyError:
            pass
        try:
            self.permalink = y['permalink']
        except KeyError:
            pass
        try:
            self.date = pytz.timezone(self.__timezone).localize(
                datetime.datetime.strptime(y['date'],date_format))
        except KeyError:
            pass
        try:
            self.updated = pytz.timezone(self.__timezone).localize(
                datetime.datetime.strptime(y['updated'],date_format))
        except KeyError:
            pass
        try:
            self.categories = set([x.strip() for x in y['categories'].split(",")])
        except:
            pass
        try:
            self.tags = set([x.strip() for x in y['tags'].split(",")])
        except:
            pass
        try:
            self.guid = y['guid']
        except KeyError:
            pass
        try:
            self.format = y['format']
        except KeyError:
            pass
        
    def permapath(self):
        """Get just the path portion of a permalink"""
        return urlparse.urlparse(self.permalink)[2]
            
def parse_posts(directory, timezone):
    """Retrieve all the posts from the directory specified.

    Returns a list of the posts sorted in reverse by date."""
    posts = []
    post_filename_re = re.compile(".*((\.textile$)|(\.markdown$)|(\.html$))")
    post_file_names = [f for f in os.listdir(directory) if post_filename_re.match(f)]
    for post_fn in post_file_names:
        src = open(os.path.join(directory,post_fn)).read()
        p = Post(src, timezone)
        #Exclude some posts
        if not (p.permalink == None):
            posts.append(p)
    posts.sort(key=operator.attrgetter('date'), reverse=True)
    return posts    

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
    
