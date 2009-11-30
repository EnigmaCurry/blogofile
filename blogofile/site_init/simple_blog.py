#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Build the absolute minimum skeleton of a blogofile based site in the current
directory"""

__author__ = "Ryan McGuire (ryan@enigmacurry.com)"
__date__   = "Tue Jul 28 22:03:21 2009"

import os
from .. import config

__base_mako = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" 
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
          ${self.body()}
        </div><!-- End Prose Block -->
        ${self.sidebar()}
      </div><!-- End Main Block -->
      <div id="footer">
        ${self.footer()}
      </div> <!-- End Footer -->
    </div> <!-- End Content -->
  </body>
</html>

<!-- These should be overridden in site.mako: -->
<%def name="head()">
</%def>
<%def name="header()">
</%def>
<%def name="footer()">
</%def>
<%def name="sidebar()">
</%def>
"""

__site_mako = """<%inherit file="base.mako" />
<%def name="head()">
  <%include file="head.mako" />
</%def>
<%def name="header()">
  <%include file="header.mako" />
</%def>
<%def name="footer()">
  <%include file="footer.mako" />
</%def>
"""

__head_mako = """<title>${bf.config.blog_name}</title>
<link rel="alternate" type="application/rss+xml" title="RSS 2.0" href="${bf.config.blog_path}/feed" />
<link rel="alternate" type="application/atom+xml" title="Atom 1.0" href="${bf.config.blog_path}/feed/atom" />
"""

__header_mako = """<h1><a href="/">${bf.config.blog_name}</a></h1>
This is a header that goes on every page.
<hr/>
"""

__footer_mako = """<hr/>This is a footer that goes on every page"""

__chronological_mako = """<%inherit file="site.mako" />
% for post in posts:
  <%include file="post.mako" args="post=post" />
  <hr/>
% endfor
% if prev_link:
 <a href="${prev_link}">« Previous Page</a>
% endif
% if prev_link and next_link:
  --  
% endif
% if next_link:
 <a href="${next_link}">Next Page »</a>
% endif
"""

__chronological_py = """# Write all the blog posts in reverse chronological order
import os

def run():
    write_blog_chron()
    write_blog_first_page()

def write_blog_chron():
    root = bf.config.blog_pagination_dir.lstrip("/")
    chron_template = bf.writer.template_lookup.get_template("chronological.mako")
    chron_template.output_encoding = "utf-8"
    page_num = 1
    post_num = 0
    html = []
    while len(bf.posts) > post_num:
        #Write the pages, num_per_page posts per page:
        page_posts = bf.posts[post_num:post_num+bf.config.blog_posts_per_page]
        post_num += bf.config.blog_posts_per_page
        if page_num > 1:
            prev_link = "../" + str(page_num - 1)
        else:
            prev_link = None
        if len(bf.posts) > post_num:
            next_link = "../" + str(page_num + 1)
        else:
            next_link = None
        page_dir = os.path.join(bf.blog_dir,root,str(page_num))
        bf.util.mkdir(page_dir)
        fn = os.path.join(page_dir,"index.html")
        f = open(fn,"w")
        html = bf.writer.template_render(
            chron_template,
            { "posts":page_posts,
              "next_link":next_link,
              "prev_link":prev_link })
        f.write(html)
        f.close()
        page_num += 1
        
def write_blog_first_page():
    if not bf.config.blog_custom_index:
        chron_template = bf.writer.template_lookup.get_template("chronological.mako")
        chron_template.output_encoding = "utf-8"
        page_posts = bf.posts[:bf.config.blog_posts_per_page]
        path = os.path.join(bf.blog_dir,"index.html")
        bf.logger.info("Writing blog index page: "+path)
        f = open(path,"w")
        if len(bf.posts) > bf.config.blog_posts_per_page:
            next_link = bf.util.blog_path_helper(bf.config.blog_pagination_dir+"/2")
        else:
            next_link = None
        html = bf.writer.template_render(
            chron_template,
            { "posts": page_posts,
              "next_link": next_link,
              "prev_link": None })
        f.write(html)
        f.close()          
"""

__rss_mako = """<?xml version="1.0" encoding="UTF-8"?><% from datetime import datetime %>
<rss version="2.0"
     xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:sy="http://purl.org/rss/1.0/modules/syndication/"
     xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:dc="http://purl.org/dc/elements/1.1/"
     xmlns:wfw="http://wellformedweb.org/CommentAPI/"
     >
  <channel>
    <title>${bf.config.blog_name}</title>
    <link>${bf.config.blog_url}</link>
    <description>${bf.config.blog_description}</description>
    <pubDate>${datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")}</pubDate>
    <generator>Blogofile</generator>
    <sy:updatePeriod>hourly</sy:updatePeriod>
    <sy:updateFrequency>1</sy:updateFrequency>
% for post in posts[:10]:
    <item>
      <title>${post.title}</title>
      <link>${post.permalink}</link>
      <pubDate>${post.date.strftime("%a, %d %b %Y %H:%M:%S %Z")}</pubDate>
% for category in post.categories:
      <category><![CDATA[${category.name}]]></category>
% endfor
% if post.guid:
      <guid>${post.guid}</guid>
% else:
      <guid isPermaLink="true">${post.permalink}</guid>
% endif
      <description>${post.title}</description>
      <content:encoded><![CDATA[${post.content}]]></content:encoded>
    </item>
% endfor
  </channel>
</rss>
"""

__atom_mako = """<?xml version="1.0" encoding="UTF-8"?><% from datetime import datetime %>
<feed
  xmlns="http://www.w3.org/2005/Atom"
  xmlns:thr="http://purl.org/syndication/thread/1.0"
  xml:lang="en"
   >
  <title type="text">${bf.config.blog_name}</title>
  <subtitle type="text">${bf.config.blog_description}</subtitle>

  <updated>${datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}</updated>
  <generator uri="http://blogofile.com/">Blogofile</generator>

  <link rel="alternate" type="text/html" href="${bf.config.blog_url}" />
  <id>${bf.config.blog_url}/feed/atom/</id>
  <link rel="self" type="application/atom+xml" href="${bf.config.blog_url}/feed/atom/" />
% for post in posts[:10]:
  <entry>
    <author>
      <name>${post.author}</name>
      <uri>${bf.config.blog_url}</uri>
    </author>
    <title type="html"><![CDATA[${post.title}]]></title>
    <link rel="alternate" type="text/html" href="${post.permalink}" />
    <id>${post.permalink}</id>
    <updated>${post.updated.strftime("%Y-%m-%dT%H:%M:%SZ")}</updated>
    <published>${post.date.strftime("%Y-%m-%dT%H:%M:%SZ")}</published>
% for category in post.categories:
    <category scheme="${bf.config.blog_url}" term="${category.name}" />
% endfor
    <summary type="html"><![CDATA[${post.title}]]></summary>
    <content type="html" xml:base="${post.permalink}"><![CDATA[${post.content}]]></content>
  </entry>
% endfor
</feed>
"""

__permapage_mako = """<%inherit file="site.mako" />
<%include file="post.mako" args="post=post" />
"""

__permapage_py = """import os
import urlparse

def run():
    "Write blog posts to their permalink locations"
    perma_template = bf.writer.template_lookup.get_template("permapage.mako")
    perma_template.output_encoding = "utf-8"
    for post in bf.posts:
        if post.permalink:
            path_parts = [bf.writer.output_dir]
            path_parts.extend(urlparse.urlparse(
                    post.permalink)[2].lstrip("/").split("/"))
            path = os.path.join(*path_parts)
            bf.logger.info("Writing permapage for post: "+path)
        else:
            #Permalinks MUST be specified. No permalink, no page.
            bf.logger.info("Post has no permalink: "+post.title)
            continue
        try:
            bf.util.mkdir(path)
        except OSError:
            pass
        html = bf.writer.template_render(
            perma_template,
            { "post": post,
              "posts": bf.posts })
        f = open(os.path.join(path,"index.html"), "w")
        f.write(html)
        f.close()
"""

__post_mako = """<%page args="post"/>
<div class="blog_post">
  <a name="${post.title}" />
  <h2 class="blog_post_title"><a href="${post.permapath()}" rel="bookmark" title="Permanent Link to ${post.title}">${post.title}</a></h2>
  <small>${post.date.strftime("%B %d, %Y at %I:%M %p")} | categories: 
<% 
   category_links = []
   for category in post.categories:
       if post.draft:
           #For drafts, we don't write to the category dirs, so just write the categories as text
           category_links.append(category.name)
       else:
           category_links.append("<a href='"+category.path+"'>"+category.name+"</a>")
%>
${", ".join(category_links)}
</small><p/>
  <span class="post_prose">
    ${post.content}
  </span>
</div>
"""

__index_mako = """<%inherit file="_templates/site.mako" />
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

__post_1 = """
---
categories: Category 1
date: 2009/07/23 15:22:00
format: markdown
permalink: http://www.your-full-site-url.com/blog/2009/07/23/post-one
title: Post 1
---
This is post #1"""

__post_2 = """
---
categories: Category 1, Category 2
date: 2009/07/24 16:20:00
format: markdown
permalink: http://www.your-full-site-url.com/blog/2009/07/24/post-two
title: Post 2
---
This is post #2"""

__post_3 = """
---
categories: Unicode
date: 2009/08/22 15:22:00
format: markdown
permalink: http://www.your-full-site-url.com/blog/2009/08/22/Unicode
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

__post_4 = """
---
categories: General Stuff
date: 2009/08/29 15:22:00
format: markdown
permalink: http://www.your-full-site-url.com/blog/2009/08/29/post-four
title: Post 4
---
This is post #4"""

__post_5 = """
---
categories: General Stuff
date: 2009/08/29 15:23:00
format: markdown
permalink: http://www.your-full-site-url.com/blog/2009/08/29/post-five
title: Post 5
---
This is post #5"""

__post_6 = """
---
categories: General Stuff
date: 2009/08/29 15:24:00
format: markdown
permalink: http://www.your-full-site-url.com/blog/2009/08/29/post-six
title: Post 6
---
This is post #6"""

__post_7 = """
---
categories: General Stuff
date: 2009/08/29 15:25:00
format: markdown
permalink: http://www.your-full-site-url.com/blog/2009/08/29/post-seven
title: Post 7
---
This is post #7"""

__setup_el = """;;; add load path for orgmode
;;;    and intialize code and prehandling routine
(setq load-path (cons "~/path/to/orgdir/lisp" load-path))
(require 'org-install)
(add-to-list 'auto-mode-alist '("\\.org$" . org-mode))
"""

def do_init(options):
    config_f = open("_config.py","w")
    config_f.write(config.default_config)
    config_f.close()
    os.mkdir("_templates")
    #Write reusable templates
    t = open(os.path.join("_templates","base.mako"),"w")
    t.write(__base_mako)
    t.close()
    t = open(os.path.join("_templates","site.mako"),"w")
    t.write(__site_mako)
    t.close()
    t = open(os.path.join("_templates","head.mako"),"w")
    t.write(__head_mako)
    t.close()
    t = open(os.path.join("_templates","header.mako"),"w")
    t.write(__header_mako)
    t.close()
    t = open(os.path.join("_templates","footer.mako"),"w")
    t.write(__footer_mako)
    t.close()
    t = open(os.path.join("_templates","chronological.mako"),"w")
    t.write(__chronological_mako)
    t.close()
    t = open(os.path.join("_templates","chronological.py"),"w")
    t.write(__chronological_py)
    t.close()
    t = open(os.path.join("_templates","rss.mako"),"w")
    t.write(__rss_mako)
    t.close()
    t = open(os.path.join("_templates","atom.mako"),"w")
    t.write(__atom_mako)
    t.close()
    t = open(os.path.join("_templates","permapage.mako"),"w")
    t.write(__permapage_mako)
    t.close()
    t = open(os.path.join("_templates","permapage.py"),"w")
    t.write(__permapage_py)
    t.close()
    t = open(os.path.join("_templates","post.mako"),"w")
    t.write(__post_mako)
    t.close()
    #Write index page
    i = open("index.html.mako","w")
    i.write(__index_mako)
    i.close()
    #Write posts
    os.mkdir("_posts")
    p = open(os.path.join("_posts","001 - post #1.markdown"),"w")
    p.write(__post_1)
    p.close()
    p = open(os.path.join("_posts","002 - post #2.markdown"),"w")
    p.write(__post_2)
    p.close()
    p = open(os.path.join("_posts","003 - post #3.markdown"),"w")
    p.write(__post_3)
    p.close()
    p = open(os.path.join("_posts","004 - post #4.markdown"),"w")
    p.write(__post_4)
    p.close()
    p = open(os.path.join("_posts","005 - post #5.markdown"),"w")
    p.write(__post_5)
    p.close()
    p = open(os.path.join("_posts","006 - post #6.markdown"),"w")
    p.write(__post_6)
    p.close()
    p = open(os.path.join("_posts","007 - post #7.markdown"),"w")
    p.write(__post_7)
    p.close()
    #Write orgmode helpers
    os.mkdir("_emacs")
    p = open(os.path.join("_emacs","setup.el"),"w")
    p.write(__setup_el)
    p.close()
    
