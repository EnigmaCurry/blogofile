#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Build the absolute minimum skeleton of a blogofile based site in the current
directory"""

__author__ = "Ryan McGuire (ryan@enigmacurry.com)"
__date__   = "Tue Jul 28 22:03:21 2009"

import os
import blog_features
from .. import config
from . import write_file

site_mako = """
"""

header_mako = """
"""

index_mako = """
"""

post_1 = """"""

post_2 = """
"""

post_3 = """
"""

post_4 = """
"""

post_5 = """
"""

post_6 = """
"""

post_7 = """
"""

syntax_highlight_post = """
"""

def do_init(options):
    write_file(("_config.py",),config.default_config)
    #Write reusable templates
    write_file(("_templates","base.mako"),blog_features.base_mako)
    write_file(("_templates","site.mako"),site_mako)
    write_file(("_templates","head.mako"),blog_features.head_mako)
    write_file(("_templates","header.mako"),header_mako)
    write_file(("_templates","footer.mako"),blog_features.footer_mako)
    write_file(("_templates","chronological.mako"),blog_features.chronological_mako)
    write_file(("_templates","rss.mako"),blog_features.rss_mako)
    write_file(("_templates","atom.mako"),blog_features.atom_mako)
    write_file(("_templates","permapage.mako"),blog_features.permapage_mako)
    write_file(("_templates","post.mako"),blog_features.post_mako)
    #Write controllers
    write_file(("_controllers","blog","__init__.py"),blog_features.init_py)
    write_file(("_controllers","blog","archives.py"),blog_features.archives_py)
    write_file(("_controllers","blog","categories.py"),blog_features.categories_py)
    write_file(("_controllers","blog","chronological.py"),blog_features.chronological_py)
    write_file(("_controllers","blog","feed.py"),blog_features.feed_py)
    write_file(("_controllers","blog","permapage.py"),blog_features.permapage_py)
    #Write filters
    write_file(("_filters","markdown.py"),blog_features.markdown_py)
    write_file(("_filters","textile.py"),blog_features.textile_py)
    write_file(("_filters","syntax_highlight.py"),blog_features.syntax_highlight_py)
    write_file(("_filters","rst.py"),blog_features.rst_py)
    #Write index page
    write_file(("index.html.mako",),index_mako)
    #Write posts
    write_file(("_posts","001 - post #1.markdown"),post_1)
    write_file(("_posts","002 - post #2.markdown"),post_2)
    write_file(("_posts","003 - post #3.markdown"),post_3)
    write_file(("_posts","004 - post #4.markdown"),post_4)
    write_file(("_posts","005 - post #5.markdown"),post_5)
    write_file(("_posts","006 - post #6.markdown"),post_6)
    write_file(("_posts","007 - post #7.markdown"),post_7)
    write_file(("_posts","008 - syntax highlight test.markdown"),
               syntax_highlight_post)
    
