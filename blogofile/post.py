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
import hashlib
import codecs

import pytz
import yaml
import logging
import BeautifulSoup

import config
import util
from cache import bf

#Markdown logging is noisy, pot it down:
logging.getLogger("MARKDOWN").setLevel(logging.ERROR)
logger = logging.getLogger("blogofile.post")

date_format = "%Y/%m/%d %H:%M:%S"

# These are all the Blogofile reserved field names for posts. It is not
# recommended that users re-use any of these field names for purposes other than the
# one stated.
reserved_field_names = {
    "title"      :"A one-line free-form title for the post",
    "date"       :"The date that the post was originally created",
    "updated"    :"The date that the post was last updated",
    "categories" :"A list of categories that the post pertains to, each seperated by commas",
    "tags"       :"A list of tags that the post pertains to, each seperated by commas",
    "permalink"  :"The full permanent URL for this post. Automatically created if not provided",
    "guid"       :"A unique hash for the post, if not provided it is assumed that the permalink is the guid",
    "author"     :"The name of the author of the post",
    "filters"    :"The filter chain to apply to the entire post. If not specified, a "
                  "default chain based on the file extension is applied. If set to "
                  "'None' it disables all filters, even default ones.",
    "filter"     :"synonym for filters",
    "draft"      :"If 'true' or 'True', the post is considered to be only a draft and not to be published.",
    "source"     :"Reserved internally",
    "yaml"       :"Reserved internally",
    "content"    :"Reserved internally",
    "filename"   :"Reserved internally"
    }

class PostParseException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
        
class Post:
    """
    Class to describe a blog post and associated metadata
    """
    def __init__(self, source, filename="Untitled"):
        self.source     = source
        self.yaml       = None
        self.title      = None
        self.__timezone = config.blog_timezone
        self.date       = None
        self.updated    = None
        self.categories = set()
        self.tags       = set()
        self.permalink  = None
        self.content    = u""
        self.excerpt    = u""
        self.filename   = filename
        self.author     = ""
        self.guid       = None
        self.draft      = False
        self.filters    = None
        self.__parse()
        self.__post_process()
        
    def __repr__(self): #pragma: no cover
        return "<Post title='%s' date='%s'>" % \
            (self.title, self.date.strftime("%Y/%m/%d %H:%M:%S"))
            
    def __parse(self):
        """Parse the yaml and fill fields"""
        yaml_sep = re.compile("^---$", re.MULTILINE)
        content_parts = yaml_sep.split(self.source, maxsplit=2)
        if len(content_parts) < 2:
            raise PostParseException(self.filename+": Post has no YAML section")
        else:
            #Extract the yaml at the top
            self.__parse_yaml(content_parts[1])
            post_src = content_parts[2]
        self.__apply_filters(post_src)
        #Do post excerpting
        self.__parse_post_excerpting()

    def __apply_filters(self, post_src):
        """Apply filters to the post"""
        #Apply block level filters (filters on only part of the post)
        # TODO: block level filters on posts
        #Apply post level filters (filters on the entire post)
        #If filter is unspecified, use the default filter based on
        #the file extension:
        if self.filters == None:
            try:
                file_extension = os.path.splitext(self.filename)[-1][1:]
                self.filters = bf.config.blog_post_default_filters[
                    file_extension]
            except KeyError:
                self.filters = []
        self.content = bf.filter.run_chain(self.filters, post_src)
        
    def __parse_post_excerpting(self):
        if config.post_excerpt_enabled:
            try:
                self.excerpt = config.post_excerpt(
                    self.content,config.post_excerpt_word_length)
            except AttributeError:
                self.excerpt = self.__excerpt(config.post_excerpt_word_length)

    def __excerpt(self, num_words=50):
        #Default post excerpting function
        #Can be overridden in _config.py by
        #defining post_excerpt(content,num_words)
        if len(self.excerpt) == 0:
             """Retrieve excerpt from article"""
             s = BeautifulSoup.BeautifulSoup(self.content)
             # get rid of javascript, noscript and css
             [[tree.extract() for tree in s(elem)] for elem in (
                     'script','noscript','style')]
             # get rid of doctype
             subtree = s.findAll(text=re.compile("DOCTYPE|xml"))
             [tree.extract() for tree in subtree]
             # remove headers
             [[tree.extract() for tree in s(elem)] for elem in (
                     'h1','h2','h3','h4','h5','h6')]
             text = ''.join(s.findAll(text=True))\
                                 .replace("\n","").split(" ")
             return " ".join(text[:num_words]) + '...'
        
    def __post_process(self):
        # fill in empty default value
        if not self.title:
            self.title      = u"Untitled - " + \
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        if not self.date:
            self.date       = datetime.datetime.now(pytz.timezone(self.__timezone))
        if not self.updated:
            self.updated    = self.date
            
        if not self.categories or len(self.categories) == 0:
            self.categories = set([Category('Uncategorized')])
        if not self.permalink and config.blog_auto_permalink_enabled:
            self.permalink = config.site_url.rstrip("/")+config.blog_auto_permalink
            self.permalink = re.sub(":year",  self.date.strftime("%Y"),
                                    self.permalink)
            self.permalink = re.sub(":month",  self.date.strftime("%m"),
                                    self.permalink)
            self.permalink = re.sub(":day",  self.date.strftime("%d"),
                                    self.permalink)
            self.permalink = re.sub(":title",
                                    self.title.replace(' ', '-').lower(),
                                    self.permalink)

            self.permalink = re.sub(
                ":filename",  self.filename.replace(' ', '-').lower(),
                self.permalink)

            # Generate sha hash based on title
            self.permalink = re.sub(":uuid",  hashlib.sha1(
                    self.title.encode('utf-8')).hexdigest(), self.permalink)
            
            self.path = urlparse.urlparse(self.permalink).path
            
        logger.debug("Permalink: %s" % self.permalink)
        
    def __parse_yaml(self, yaml_src):
        y = yaml.load(yaml_src)
        # Load all the fields that require special processing first:
        fields_need_processing = ('permalink','guid','date','updated',
                                  'categories','tags','draft')
        try:
            self.permalink = y['permalink']
            if self.permalink.startswith("/"):
                self.permalink = urlparse.urljoin(config.site_url,self.permalink)
            #Ensure that the permalink is for the same site as bf.config.site_url
            if not self.permalink.startswith(bf.config.site_url):
                raise PostParseException(self.filename+": permalink for a different site"
                                         " than configured")
            self.path = urlparse.urlparse(self.permalink).path
            logger.debug("path from permalink: "+self.path)
        except KeyError:
            pass
        try:
            self.guid = y['guid']
        except KeyError:
            self.guid = self.permalink
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
            self.categories = set([Category(x.strip()) for x in \
                                       y['categories'].split(",")])
        except:
            pass
        try:
            self.tags = set([x.strip() for x in y['tags'].split(",")])
        except:
            pass
        try:
            self.filters = y['filter'] #filter is a synonym for filters
        except KeyError:
            pass
        try:
            if y['draft']:
                self.draft = True
                logger.info("Post "+self.filename+
                            " is set to draft, ignoring this post")
            else:
                self.draft = False
        except KeyError:
            self.draft = False
        # Load the rest of the fields that don't need processing:
        for field, value in y.items():
            if field not in fields_need_processing:
                setattr(self,field,value)
        
    def permapath(self):
        """Get just the path portion of a permalink"""
        return urlparse.urlparse(self.permalink)[2]

class Category:
    def __init__(self, name):
        self.name = unicode(name)
        self.url_name = self.name.lower().replace(" ","-")
        self.path = util.site_path_helper(config.blog_path,config.blog_category_dir,self.url_name)
    def __eq__(self, other):
        if self.name == other.name:
            return True
        else:
            return False
    def __hash__(self):
        return hash(self.name)
    def __repr__(self):
        return self.name
    def __cmp__(self, other):
        return cmp(self.name, other.name)

def parse_posts(directory):
    """Retrieve all the posts from the directory specified.

    Returns a list of the posts sorted in reverse by date."""
    posts = []
    post_filename_re = re.compile(
        ".*((\.textile$)|(\.markdown$)|(\.org$)|(\.html$)|(\.txt$)|(\.rst$))")
    if not os.path.isdir("_posts"):
        logger.warn("This site has no _posts directory.")
        return []
    post_paths = [f for f in util.recursive_file_list(
            directory, post_filename_re) if post_filename_re.match(f)]
    
    for post_path in post_paths:
        post_fn = os.path.split(post_path)[1]
        logger.debug("Parsing post: %s" % post_path)
        #IMO codecs.open is broken on Win32.
        #It refuses to open files without replacing newlines with CR+LF
        #reverting to regular open and decode:
        src = open(post_path,"r").read().decode(config.blog_post_encoding)
        try:
            p = Post(src, filename=post_fn)
        except PostParseException as e:
            logger.warning(e.value+" : Skipping this post.")
            continue
        #Exclude some posts
        if not (p.permalink == None or p.draft == True):
            posts.append(p)
    posts.sort(key=operator.attrgetter('date'), reverse=True)
    return posts
