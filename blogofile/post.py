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
import logging
import BeautifulSoup
import org

from main import logger
import config

#Markdown logging is noisy, pot it down:
logging.getLogger("MARKDOWN").setLevel(logging.ERROR)

import util

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
    def __init__(self, source, format="html"):
        self.source     = source
        self.yaml       = yaml
        self.title      = None
        self.__timezone = config.blog_timezone
        self.date       = datetime.datetime.now(pytz.timezone(self.__timezone))
        self.updated    = self.date
        self.categories = set()
        self.tags       = set()
        self.permalink  = None
        self.content    = u""
        self.excerpt    = u""
        self.format     = format
        self.author     = ""
        self.guid       = None #Default guid is permalink
        self.draft      = False
        self.__parse()
        self.__post_process()
        
    def __repr__(self):
        return "<Post title='%s' date='%s'>" % \
            (self.title, self.date.strftime("%Y/%m/%d %H:%M:%S"))
        
    def __parse(self):
        """Parse the yaml and fill fields"""
        yaml_sep = re.compile("^---$", re.MULTILINE)
        content_parts = yaml_sep.split(self.source, maxsplit=2)
        if len(content_parts) < 2:
            #No yaml to extract
            post_src = self.source
        else:
            #Extract the yaml at the top
            self.__parse_yaml(content_parts[1])
            post_src = content_parts[2]
        #Convert post to HTML
        if self.format == "textile":
            self.content = textile.textile(post_src)
        elif self.format == "markdown":
            self.content = markdown.markdown(post_src)
        elif self.format == "html":
            self.content = post_src
        elif self.format == "org":
            if config.orgmode_enabled:
                org_info = org.org(post_src)
                # content field
                self.content = org_info.content
                # if title is not set, extracted '*' head is used for title
                if not self.title:
                    self.title   = org_info.title
                # if categories is not set, extracted "*"'s tag is used for categories
                if not org_info.categories:
                    self.categories = org_info.categories
            else:
                self.content = post_src
        else:
            raise PostFormatException("Post format '%s' not recognized." %
                                      self.format)

        self.content = self.content.decode("utf-8")

        #Do syntax highlighting of <pre> tags
        if config.syntax_highlight_enabled:
            self.content = util.do_syntax_highlight(self.content,config)
        #Do post excerpting
        if config.post_excerpt_enabled:
            try:
                self.excerpt = config.post_excerpt(
                    self.content,config.post_excerpt_word_length)
            except AttributeError:
                self.excerpt = self.__excerpt(config.post_excerpt_word_length)

    def __post_process(self):
        # fill in empty default value
        if not self.title:
            self.title      = u"Untitled - " + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        if not self.categories:
            self.categories = set([u'Uncategorized'])
        if not self.permalink:
            self.permalink = config.permalink

            self.permalink = re.sub(":year",  self.date.strftime("%Y"), self.permalink)
            self.permalink = re.sub(":month",  self.date.strftime("%m"), self.permalink)
            self.permalink = re.sub(":day",  self.date.strftime("%d"), self.permalink)
            self.permalink = re.sub(":title",  self.title.replace(' ', '-'), self.permalink)

            import uuid
            self.permalink = re.sub(":uuid",  str(uuid.uuid4()), self.permalink)
            self.permalink = self.permalink.lower()
                
    def __excerpt(self, num_words=50):
        #Default post excerpting function
        #Can be overridden in _config.py by
        #defining post_excerpt(content,num_words)
        if len(self.excerpt) == 0:
             """Retrieve excerpt from article"""
             s = BeautifulSoup.BeautifulSoup(self.content)
             # get rid of javascript, noscript and css
             [[tree.extract() for tree in s(elem)] for elem in ('script','noscript','style')]
             # get rid of doctype
             subtree = s.findAll(text=re.compile("DOCTYPE|xml"))
             [tree.extract() for tree in subtree]
             # remove headers
             [[tree.extract() for tree in s(elem)] for elem in ('h1','h2','h3','h4','h5','h6')]
             text = ''.join(s.findAll(text=True))\
                                 .replace("\n","").split(" ")
             return " ".join(text[:num_words]) + '...'
        
    def __parse_yaml(self, yaml_src):
        y = yaml.load(yaml_src)
        try:
            self.title = y['title']
        except KeyError:
            pass
        try:
            self.permalink = y['permalink']
            self.path = urlparse.urlparse(self.permalink).path
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
            self.categories = set([x.strip() for x in \
                                       y['categories'].split(",")])
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

def parse_posts(directory):
    """Retrieve all the posts from the directory specified.

    Returns a list of the posts sorted in reverse by date."""
    posts = []
    # post_filename_re = re.compile(".*((\.textile$)|(\.markdown$)|(\.html$))")
    post_filename_re = re.compile(".*(\.org$)")
    post_file_names = [f for f in os.listdir(directory) \
                           if post_filename_re.match(f)]
    for post_fn in post_file_names:
        post_path = os.path.join(directory,post_fn)
        logger.info("Parsing post: %s" % post_path)
        src = open(post_path).read()
        p = Post(src, format=os.path.splitext(post_path)[1][1:])
        #Exclude some posts
        if not (p.permalink == None):
            posts.append(p)
    posts.sort(key=operator.attrgetter('date'), reverse=True)
    return posts    

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
    
