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
import textile
import markdown
import logging
import BeautifulSoup
import org

import config
import util

#Markdown logging is noisy, pot it down:
logging.getLogger("MARKDOWN").setLevel(logging.ERROR)
logger = logging.getLogger("blogofile.post")

date_format = "%Y/%m/%d %H:%M:%S"

# These are all the Blogofile reserved field names for posts. It is not
# recommended that users re-use any of these field names for purposes other than the
# one stated.
reserved_field_names = {
    "title"      :"A one-line free form title for the post",
    "date"       :"The date that the post was originally created",
    "updated"    :"The date that the post was last updated",
    "categories" :"A list of categories that the post pertains to, each seperated by commas",
    "tags"       :"A list of tags that the post pertains to, each seperated by commas",
    "permalink"  :"The full permanent URL for this post. Automatically created if not provided",
    "format"     :"The format of the post (eg: html, textile, markdown, org)",
    "guid"       :"A unique hash for the post, if not provided it is assumed that the permalink is the guid",
    "author"     :"The name of the author of the post",
    "draft"      :"If 'true' or 'True', the post is considered to be only a draft and not to be published.",
    "source"     :"Reserved internally",
    "yaml"       :"Reserved internally",
    "content"    :"Reserved internally",
    "filename"   :"Reserved internally"
    }

class PostFormatException(Exception):
    pass

class Post:
    """
    Class to describe a blog post and associated metadata
    """
    def __init__(self, source, filename="Untitled", format="html"):
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
        self.format     = format
        self.filename   = filename
        self.author     = ""
        self.guid       = None
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
            logger.warn("Post "+self.filename+" has no YAML section!")
            post_src = self.source
        else:
            #Extract the yaml at the top
            self.__parse_yaml(content_parts[1])
            post_src = content_parts[2]
        #Convert post to HTML
        self.__parse_format(post_src)
        #Do syntax highlighting of <pre> tags
        self.__parse_syntax_highlight()
        #Do post excerpting
        self.__parse_post_excerpting()

    def __parse_format(self, post_src):
        if self.format == "textile":
            self.content = textile.textile(post_src)
        elif self.format == "markdown":
            self.content = markdown.markdown(post_src)
        elif self.format == "html":
            self.content = post_src
        elif self.format == "org":
            if config.emacs_orgmode_enabled:
                org_info = org.org(post_src)
                # content field
                self.content = org_info.content
                # if title is not set, extract the first head as title 
                if not self.title:
                    self.title   = org_info.title
                # if categories is not set, extract the first head's tag as categories
                if not self.categories:
                    self.categories = org_info.categories
                # if date is not set, extract the first head's timestamp as date
                if not self.date:
                    self.date = org_info.date
            else:
                self.content = post_src
        else:
            raise PostFormatException("Post format '%s' not recognized." %
                                      self.format)
        
    def __parse_syntax_highlight(self):
        if config.syntax_highlight_enabled:
            self.content = util.do_syntax_highlight(self.content,config)

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
            self.permalink = urlparse.urljoin(config.site_url,config.blog_auto_permalink)

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
            self.path = urlparse.urlparse(self.permalink).path
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
            if y['draft'].strip().lower() == "true":
                self.draft = True
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
        url = unicode(urlparse.urljoin(config.site_url,"/".join((config.blog_path,config.blog_category_dir,self.url_name))))
        self.path = urlparse.urlparse(url).path
    def __eq__(self, other):
        if self.name == other.name:
            return True
        else:
            return False
    def __hash__(self):
        return hash(self.name)
    def __repr__(self):
        return self.name
                                  
def parse_posts(directory):
    """Retrieve all the posts from the directory specified.

    Returns a list of the posts sorted in reverse by date."""
    posts = []
    post_filename_re = re.compile(
        ".*((\.textile$)|(\.markdown$)|(\.org$)|(\.html$))")
    if not os.path.isdir("_posts"):
        logger.error("There is no _posts directory")
        return []
    post_file_names = [f for f in os.listdir(directory) \
                           if post_filename_re.match(f)]
    for post_fn in post_file_names:
        post_path = util.path_join(directory,post_fn)
        logger.debug("Parsing post: %s" % post_path)
        #IMO codecs.open is broken on Win32.
        #It refuses to open files without replacing newlines with CR+LF
        #reverting to regular open and decode:
        src = open(post_path,"r").read().decode(config.blog_post_encoding)
        p = Post(src, filename=os.path.splitext(post_fn)[0],
                 format=os.path.splitext(post_fn)[1][1:])
        #Exclude some posts
        if not (p.permalink == None):
            posts.append(p)
    posts.sort(key=operator.attrgetter('date'), reverse=True)
    return posts    
