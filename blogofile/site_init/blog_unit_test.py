#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This site is only used for unit tests"""

__author__ = "Ryan McGuire (ryan@enigmacurry.com)"
__date__   = "Tue Jul 28 22:03:21 2009"

import os
import blog_features
from .. import config
from . import write_file

site_mako = """<%inherit file="base.mako" />
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" 
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    ${self.head()}
  </head>
  <body>
    <div id="content">
      ${self.header()}
      <div id="main_block">
        <div id="prose_block">
          ${next.body()}
        </div><!-- End Prose Block -->
      </div><!-- End Main Block -->
      <div id="footer">
        ${self.footer()}
      </div> <!-- End Footer -->
    </div> <!-- End Content -->
  </body>
</html>
<%def name="head()">
  <%include file="head.mako" />
</%def>
<%def name="header()">
  <%include file="header.mako" />
</%def>
<%def name="footer()">
  <hr/>
  This is a footer that appears on every page.
  <%include file="footer.mako" />
</%def>
"""

header_mako = """<h1><a href="/">${bf.config.blog_name}</a></h1>
<p>This is a simple blog build with Blogofile.</p>
<p>It's completely unthemed and is written as minimally as possible, while still
retaining most of the blog features.</p>
<p>Make sure you read the <a href="http://www.blogofile.com/documentation">online
documentation</a>.</p>
<p>If you're looking for a more fleshed-out site try running 'blogofile init
blogofile.com', but you'll need <a href="http://www.git-scm.org">git</a> installed first.</p>
<p>This is a header that goes on every page.</p>
<hr/>
"""

index_mako = """<%inherit file="_templates/site.mako" />
<p>
 This is the index page.
</p>

Here's the main <a href="${bf.config.blog_path}">chronological blog page</a><br/><br/>

Here's the last 5 posts:
<ul>
% for post in bf.posts[:5]:
    <li><a href="${post.path}">${post.title}</a></li>
% endfor
</ul>
"""

post_1 = """
---
categories: Category 1
date: 2009/07/23 15:22:00
format: markdown
title: Post 1
---
This is post #1"""

post_2 = """
---
categories: Category 1, Category 2
date: 2009/07/24 16:20:00
format: markdown
title: Post 2
---
This is post #2"""

post_3 = """
---
categories: Unicode
date: 2009/08/22 15:22:00
format: markdown
permalink: http://www.yoursite.com/blog/2009/08/22/Unicode
title: Post 3 - Unicode Test
---
Anglo-Saxon Rune Poem:

ᚠᛇᚻ᛫ᛒᛦᚦ᛫ᚠᚱᚩᚠᚢᚱ᛫ᚠᛁᚱᚪ᛫ᚷᛖᚻᚹᛦᛚᚳᚢᛗ
ᛋᚳᛖᚪᛚ᛫ᚦᛖᚪᚻ᛫ᛗᚪᚾᚾᚪ᛫ᚷᛖᚻᚹᛦᛚᚳ᛫ᛗᛁᚳᛚᚢᚾ᛫ᚻᛦᛏ᛫ᛞᚫᛚᚪᚾ
ᚷᛁᚠ᛫ᚻᛖ᛫ᚹᛁᛚᛖ᛫ᚠᚩᚱ᛫ᛞᚱᛁᚻᛏᚾᛖ᛫ᛞᚩᛗᛖᛋ᛫ᚻᛚᛇᛏᚪᚾ᛬

Tamil poetry:

யாமறிந்த மொழிகளிலே தமிழ்மொழி போல் இனிதாவது எங்கும் காணோம்,
பாமரராய் விலங்குகளாய், உலகனைத்தும் இகழ்ச்சிசொலப் பான்மை கெட்டு,
நாமமது தமிழரெனக் கொண்டு இங்கு வாழ்ந்திடுதல் நன்றோ? சொல்லீர்!
தேமதுரத் தமிழோசை உலகமெலாம் பரவும்வகை செய்தல் வேண்டும்.


I can eat glass:
私はガラスを食べられます。それは私を傷つけません。
Կրնամ ապակի ուտել և ինծի անհանգիստ չըներ։
I kå Glas frässa, ond des macht mr nix!
᚛᚛ᚉᚑᚅᚔᚉᚉᚔᚋ ᚔᚈᚔ ᚍᚂᚐᚅᚑ ᚅᚔᚋᚌᚓᚅᚐ᚜
אני יכול לאכול זכוכית וזה לא מזיק לי
काचं शक्नोम्यत्तुम् । नोपहिनस्ति माम् ॥ 

"""

post_4 = """
---
categories: General Stuff
date: 2009/08/29 15:22:00
format: markdown
permalink: http://www.yoursite.com/blog/2009/08/29/post-four
title: Post 4
---
This is post #4"""

post_5 = """
---
categories: General Stuff
date: 2009/08/29 15:23:00
format: markdown
permalink: http://www.yoursite.com/blog/2009/08/29/post-five
title: Post 5
---
This is post #5"""

post_6 = """
---
categories: General Stuff
date: 2009/08/29 15:24:00
format: markdown
permalink: http://www.yoursite.com/blog/2009/08/29/post-six
title: Post 6
---
This is post #6"""

post_7 = """
---
categories: General Stuff
date: 2009/08/29 15:25:00
format: markdown
permalink: http://www.yoursite.com/blog/2009/08/29/post-seven
title: Post 7
---
This is post #7"""

post_no_yaml = """This post has no YAML section oh noes!

Yea, this should produce a warning message."""

post_no_title = """
---
categories: General Stuff
date: 2009/08/29 15:25:00
format: markdown
permalink: http://www.yoursite.com/blog/2009/08/29/post-no-title
---
This post has no title"""

post_no_date = """
---
categories: General Stuff
format: markdown
title: Post without a date
---
This post has no date"""

post_no_permalink = """
---
categories: General Stuff
date: 2009/08/29 15:25:00
format: markdown
title: Post without a permalink
---
This post has no permalink"""

post_draft = """
---
categories: General Stuff
date: 2009/08/29 15:25:00
format: markdown
title: This post is a DRAFT.
draft: true
---
This post is a draft and should never be rendered"""

post_with_no_filter = """
---
categories: General Stuff
date: 2009/08/29 15:25:00
format: markdown
title: This post has no filter
permalink: http://www.yoursite.com/blog/2009/08/29/post-without-filters
filter: None
---
This post is not run through any filters"""

post_in_subdir = """
---
categories: General Stuff
date: 2009/08/29 15:25:01
format: markdown
title: This post was in a subdirectory
permalink: http://www.yoursite.com/blog/2009/08/29/post-in-subdir
filter: None
---
This post is in a subdirectory of /_posts"""


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
    write_file(("_controllers","0.initial.py"),blog_features.initial_py)
    write_file(("_controllers","archives.py"),blog_features.archives_py)
    write_file(("_controllers","categories.py"),blog_features.categories_py)
    write_file(("_controllers","chronological.py"),blog_features.chronological_py)
    write_file(("_controllers","feed.py"),blog_features.feed_py)
    write_file(("_controllers","permapage.py"),blog_features.permapage_py)
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
    write_file(("_posts","008 - post with no yaml.markdown"),post_no_yaml)
    write_file(("_posts","009 - post with no title.markdown"),post_no_title)
    write_file(("_posts","010 - post with no date.markdown"),post_no_date)
    write_file(("_posts","011 - post with no permalink.markdown"),post_no_permalink)
    write_file(("_posts","012 - post draft.markdown"),post_draft)
    write_file(("_posts","013 - post with no filter.markdown"),post_with_no_filter)
    write_file(("_posts","a_subdir","014 - post in a subdirectory.markdown"),
               post_in_subdir)
