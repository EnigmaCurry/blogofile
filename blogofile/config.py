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

default_config = """######################################################################
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
#Your Blog's name. This is used repeatedly in default blog templates
blog_name        = "Your Blog's Name"
#Your Blog's full URL
blog_url         = "http://www.your-blogs-full-url.com/path/to/blog"
#A short one line description of the blog, used in the RSS/Atom feeds.
blog_description = "Your Blog's short description"
#The timezone that you normally write your blog posts from
blog_timezone    = "US/Eastern"

######################################################################
# Intermediate Settings
######################################################################
#### Disqus.com comment integration ####
disqus_enabled = True
disqus_name    = "blogofile"

#### Blog post syntax highlighting ####
syntax_highlight_enabled = True
# You can change the style to any builtin Pygments style
# or, make your own: http://pygments.org/docs/styles
syntax_highlight_style   = "murphy"

#Post excerpts
#If you want to generate excerpts of your posts in addition to the
#full post content turn this feature on
post_excerpt_enabled     = True
post_excerpt_word_length = 25
#Also, if you don't like the way the post excerpt is generated
#You can define a new function
#below called post_excerpt(content, num_words)

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
            style=syntax_highlight_style)
    #Compile ignore_patterns
    import re
    global compiled_ignore_patterns
    compiled_ignore_patterns = []
    for p in ignore_patterns:
        if type(p) in (str,unicode):
            compiled_ignore_patterns.append(re.compile(p,re.IGNORECASE))
        else:
            compiled_ignore_patterns.append(p)
            
def __load_config():
    #Strategy: Load the default config, and then the user's config.
    #This will make sure that we have good default values if the user's
    #config is missing something.
    exec(default_config)
    execfile(__path)
    #config is now in locals() but needs to be in globals()
    for k,v in locals().items():
        globals()[k] = v
    __post_load_tasks()
    __loaded = True
    
def init(config_file_path):
    if not os.path.isfile(config_file_path):
        raise ConfigNotFoundException
    global __path
    __path = config_file_path
    __load_config()
