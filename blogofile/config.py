#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This loads the user's _config.py file and provides a standardized interface
into it."""

__author__ = "Ryan McGuire (ryan@enigmacurry.com)"
__date__   = "Tue Jul 28 20:40:29 2009"

import os
import sys

import post
import util
import writer
import blogofile_bf as bf
import cache
import controller

bf.config = sys.modules['blogofile.config']

__loaded = False

class UnknownConfigSectionException(Exception):
    pass
class ConfigNotFoundException(Exception):
    pass

override_options = {} #override config options (mostly from unit tests)

#Default config sections
site = cache.HierarchicalCache()
controllers = cache.HierarchicalCache()
blog = cache.HierarchicalCache()

def section():
    "A config 'section' is just a HierarchicalCache object"
    return cache.HierarchicalCache()

default_config = r"""# -*- coding: utf-8 -*-

######################################################################
# This is the main Blogofile configuration file.
# www.Blogofile.com
#
# This file has the following ordered sections:
#  * Basic Settings
#  * Intermediate Settings
#  * Advanced Settings
#
#  You really only _need_ to change the Basic Settings.
######################################################################

#Enable blog controllers:
# TODO: refactor this into a single module:
controllers.initial.enabled = True
controllers.initial.priority = 100
controllers.archives.enabled = True
controllers.categories.enabled = True
controllers.chronological.enabled = True
controllers.feed.enabled = True
controllers.permapage.enabled = True


######################################################################
# Basic Settings
#  (almost all sites will want to configure these settings)
######################################################################
## site_url -- Your site's full URL
# Your "site" is the same thing as your _site directory.
#  If you're hosting a blogofile powered site as a subdirectory of a larger
#  non-blogofile site, then you would set the site_url to the full URL
#  including that subdirectory: "http://www.yoursite.com/path/to/blogofile-dir"
site.url         = "http://www.yoursite.com"

#### Blog Settings ####

## blog_enabled -- Should the blog be enabled?
#  (You don't _have_ to use blogofile to build blogs)
blog.enabled = True

## blog_path -- Blog path.
#  This is the path of the blog relative to the site_url.
#  If your site_url is "http://www.yoursite.com/~ryan"
#  and you set blog_path to "/blog" your full blog URL would be
#  "http://www.yoursite.com/~ryan/blog"
#  Leave blank "" to set to the root of site_url
blog.path = "/blog"

## blog_name -- Your Blog's name.
# This is used repeatedly in default blog templates
blog.name        = "Your Blog's Name"

## blog_description -- A short one line description of the blog
# used in the RSS/Atom feeds.
blog.description = "Your Blog's short description"

## blog_timezone -- the timezone that you normally write your blog posts from
blog.timezone    = "US/Eastern"

## blog_posts_per_page -- Blog posts per page
blog.posts_per_page = 5

# Automatic Permalink
# (If permalink is not defined in post article, it's generated
#  automatically based on the following format:)
# Available string replacements:
# :year, :month, :day -> post's date
# :title              -> post's title
# :uuid               -> sha hash based on title
# :filename           -> article's filename without suffix
blog.auto_permalink_enabled = True
# This is relative to site_url
blog.auto_permalink         = "/blog/:year/:month/:day/:title"

######################################################################
# Intermediate Settings
######################################################################
#### Disqus.com comment integration ####
blog.disqus.enabled = False
blog.disqus.name    = "your_disqus_name"

#### Emacs Integration ####
blog.emacs_orgmode_enabled = False
# emacs binary (orgmode must be installed)
blog.emacs_binary    = "/usr/bin/emacs"               # emacs 22 or 23 is recommended
blog.emacs_preload_elisp = "_emacs/setup.el"          # preloaded elisp file
blog.emacs_orgmode_preamble = r"#+OPTIONS: H:3 num:nil toc:nil \n:nil"   # added in preamble

#### Blog post syntax highlighting ####
site.syntax_highlight.enabled = True
# You can change the style to any builtin Pygments style
# or, make your own: http://pygments.org/docs/styles
site.syntax_highlight.style   = "murphy"

#### Custom blog index ####
# If you want to create your own index page at your blog root
# turn this on. Otherwise blogofile assumes you want the
# first X posts displayed instead
blog.custom_index = False

#### Post excerpts ####
# If you want to generate excerpts of your posts in addition to the
# full post content turn this feature on
blog.post_excerpts.enabled     = True
blog.post_excerpts.word_length = 25
#Also, if you don't like the way the post excerpt is generated
#You can define assign a new function to blog.post_excerpts.method
#This method must accept the following arguments: (content, num_words)

#### Blog pagination directory ####
# blogofile places extra pages of your blog in
# a secondary directory like the following:
# http://www.yourblog.com/blog_root/page/4
# You can rename the "page" part here:
blog.pagination_dir = "page"

#### Blog category directory ####
# blogofile places extra pages of your or categories in
# a secondary directory like the following:
# http://www.yourblog.com/blog_root/category/your-topic/4
# You can rename the "category" part here:
blog.category_dir = "category"

#### Site css directory ####
# Where to write css files generated by blogofile
# (eg, Syntax highlighter writes out a pygments.css file)
# This is relative to site_url
site.css_dir = "/css"

#### Post encoding ####
blog.post_encoding = "utf-8"

######################################################################
# Advanced Settings
######################################################################
# These are the default ignore patterns for excluding files and dirs
# from the _site directory
# These can be strings or compiled patterns.
# Strings are assumed to be case insensitive.
site.file_ignore_patterns = [
    r".*([\/]|[\\])_.*",    #All files that start with an underscore
    r".*([\/]|[\\])#.*",    #Emacs temporary files
    r".*~$",                #Emacs temporary files
    r".*([\/]|[\\])\.git$", #Git VCS dir
    r".*([\/]|[\\])\.hg$",  #Mercurial VCS dir
    r".*([\/]|[\\])\.bzr$", #Bazaar VCS dir
    r".*([\/]|[\\])\.svn$", #Subversion VCS dir
    r".*([\/]|[\\])CVS$"    #CVS dir
    ]

#### Default post filters ####
# If a post does not specify a filter chain, use the 
# following defaults based on the post file extension:
blog.post_default_filters = {
    "markdown": "syntax_highlight, markdown",
    "textile": "syntax_highlight, textile",
    "org": "syntax_highlight, org",
    "rst": "syntax_highlight, rst"
}

### Pre/Post build hooks:
def pre_build():
    #Do whatever you want before the _site is built
    pass
def post_build():
    #Do whatever you want after the _site is built
    pass
"""

def recompile():
    #Compile file_ignore_patterns
    import re
    global site
    site.compiled_file_ignore_patterns = []
    for p in site.file_ignore_patterns:
        if isinstance(p,basestring):
            site.compiled_file_ignore_patterns.append(
                re.compile(p,re.IGNORECASE))
        else:
            #p could just be a pre-compiled regex
            site.compiled_file_ignore_patterns.append(p)
    import urlparse
    global blog
    blog.url = urlparse.urljoin(site.url,blog.path)
        
def __load_config(path=None):
    #Strategy:
    # 1) Load the default config
    # 2) Load the controllers
    # 3) Finally load the user's config.
    #
    # This will ensure that we have good default values if the user's
    # config is missing something.
    exec(default_config)
    controller.load_controllers()
    if path:
        execfile(path)
    #config is now in locals() but needs to be in globals()
    for k,v in locals().items():
        globals()[k] = v
    #Override any options (from unit tests)
    for k,v in override_options.items():
        if "." in k:
            parts = k.split(".")
            cache_object = ".".join(parts[:-1])
            setting = parts[-1]
            cache_object = eval(cache_object)
            cache_object[setting] = v
        else:
            globals()[k] = v
    recompile()
    __loaded = True
    
def init(config_file_path=None):
    #Initialize the config, if config_file_path is None,
    #just load the default config
    if config_file_path:
        if not os.path.isfile(config_file_path):
            raise ConfigNotFoundException
        __load_config(config_file_path)
    else:
        __load_config()
    return globals()['__name__']
