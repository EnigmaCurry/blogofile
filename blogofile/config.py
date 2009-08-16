#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This loads the user's _config.py file and provides a standardized interface
into it."""

__author__ = "Ryan McGuire (ryan@enigmacurry.com)"
__date__   = "Tue Jul 28 20:40:29 2009"

import os

__loaded = False

class UnknownConfigSectionException(Exception):
    pass
class ConfigNotFoundException(Exception):
    pass

default_config = r"""######################################################################
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

######################################################################
# Basic Settings
#  (almost all sites will want to configure these settings)
######################################################################
#Blog enabled. (You don't _have_ to use blogofile to build blogs)
blog_enabled = True
#Your Blog's name. This is used repeatedly in default blog templates
blog_name        = "Your Blog's Name"
#Your Blog's full URL
blog_url         = "http://www.yoursite.com/blog"
#A short one line description of the blog, used in the RSS/Atom feeds.
blog_description = "Your Blog's short description"
#The timezone that you normally write your blog posts from
blog_timezone    = "US/Eastern"
#Blog posts per page
blog_posts_per_page = 5

# Automatic Permalink
# (If permalink is not defined in post article, it's generated
#  automatically based on the following format:)
# :year, :month, :day -> post's date
# :title              -> post's title
# :uuid               -> sha hash based on title
# :filename           -> article's filename without suffix
permalink        = "/blog/:filename"

######################################################################
# Intermediate Settings
######################################################################
#### Disqus.com comment integration ####
disqus_enabled = False
disqus_name    = "your_disqus_name"

#### Emacs Integration ####
emacs_orgmode_enabled = False
# emacs binary (orgmode must be installed)
emacs_binary    = "/usr/bin/emacs"               # emacs 22 or 23 is recommended
emacs_preload_elisp = "_emacs/setup.el"          # preloaded elisp file
emacs_orgmode_preamble = r"#+OPTIONS: H:3 num:nil toc:nil \n:nil"   # added in preamble

#### Blog post syntax highlighting ####
syntax_highlight_enabled = True
# You can change the style to any builtin Pygments style
# or, make your own: http://pygments.org/docs/styles
syntax_highlight_style   = "murphy"

#### Custom blog index ####
# If you want to create your own index page at your blog root
# turn this on. Otherwise blogofile assumes you want the
# first X posts displayed instead
blog_custom_index = False

#### Post excerpts ####
# If you want to generate excerpts of your posts in addition to the
# full post content turn this feature on
post_excerpt_enabled     = True
post_excerpt_word_length = 25
#Also, if you don't like the way the post excerpt is generated
#You can define a new function
#below called post_excerpt(content, num_words)

#### Blog pagination directory ####
# blogofile places extra pages of your blog in
# a secondary directory like the following:
# http://www.yourblog.com/blog_root/page/4
# You can rename the "page" part here:
blog_pagination_dir = "page"

#### Blog category directory ####
# blogofile places extra pages of your or categories in
# a secondary directory like the following:
# http://www.yourblog.com/blog_root/category/your-topic/4
# You can rename the "category" part here:
blog_category_dir = "category"

######################################################################
# Advanced Settings
######################################################################
# These are the default ignore patterns for excluding files and dirs
# from the _site directory
# These can be strings or compiled patterns.
# Strings are assumed to be case insensitive.
ignore_patterns = [
    r".*[\/]_.*",   #All files that start with an underscore
    r".*[\/]#.*",   #Emacs temporary files
    r".*~$]",       #Emacs temporary files
    r".*[\/]\.git", #Git VCS dir
    r".*[\/]\.hg",  #Mercurial VCS dir
    r".*[\/]\.bzr", #Bazaar VCS dir
    r".*[\/]\.svn", #Subversion VCS dir
    r".*[\/]CVS"    #CVS dir
    ]

### Pre/Post build hooks:
def pre_build():
    #Do whatever you want before the _site is built
    pass
def post_build():
    #Do whatever you want after the _site is built
    pass
"""

def __post_load_tasks():
    #Instantiate syntax highlighter:
    if syntax_highlight_enabled == True:
        global html_formatter
        import pygments
        html_formatter = pygments.formatters.HtmlFormatter(
            style=syntax_highlight_style, encoding='utf-8')
    #Compile ignore_patterns
    import re
    global compiled_ignore_patterns
    compiled_ignore_patterns = []
    for p in ignore_patterns:
        if type(p) in (str,unicode):
            compiled_ignore_patterns.append(re.compile(p,re.IGNORECASE))
        else:
            compiled_ignore_patterns.append(p)
    #Calculate the absoulte blog path (ie, minus the domain)
    global blog_path
    from urlparse import urlparse
    blog_path = "/"+urlparse(blog_url).path.strip("/")
    if blog_path == "/":
        blog_path = ""
            
def __load_config(path=None):
    #Strategy: Load the default config, and then the user's config.
    #This will make sure that we have good default values if the user's
    #config is missing something.
    exec(default_config)
    if path:
        execfile(path)
    #config is now in locals() but needs to be in globals()
    for k,v in locals().items():
        globals()[k] = v
    __post_load_tasks()
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
