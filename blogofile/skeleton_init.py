#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Build the absolute minimum skeleton of a blogofile based site in the current
directory"""

__author__ = "Ryan McGuire (ryan@enigmacurry.com)"
__date__   = "Tue Jul 28 22:03:21 2009"

import os
import config

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

__head_mako = """<title>${config.blog_name}</title>
<link rel="alternate" type="application/rss+xml" title="RSS 2.0" href="/feed" />
<link rel="alternate" type="application/atom+xml" title="Atom 1.0" href="/feed/atom" />
"""

__header_mako = """<h1><a href="/">${config.blog_name}</a></h1>
This is a header that goes on every page.
"""

__footer_mako = """<h3>This is a footer that goes on every page</h3>"""

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

__rss_mako = """<?xml version="1.0" encoding="UTF-8"?><% from datetime import datetime %>
<rss version="2.0"
     xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:sy="http://purl.org/rss/1.0/modules/syndication/"
     xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:dc="http://purl.org/dc/elements/1.1/"
     xmlns:wfw="http://wellformedweb.org/CommentAPI/"
     >
  <channel>
    <title>${config.blog_name}</title>
    <link>${config.blog_url}</link>
    <description>${config.blog_description}</description>
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
      <category><![CDATA[${category}]]></category>
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
  <title type="text">${config.blog_name}</title>
  <subtitle type="text">${config.blog_description}</subtitle>

  <updated>${datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}</updated>
  <generator uri="http://blogofile.com/">Blogofile</generator>

  <link rel="alternate" type="text/html" href="${config.blog_url}" />
  <id>${config.blog_url}/feed/atom/</id>
  <link rel="self" type="application/atom+xml" href="${config.blog_url}/feed/atom/" />
% for post in posts[:10]:
  <entry>
    <author>
      <name>${post.author}</name>
      <uri>${config.blog_url}</uri>
    </author>
    <title type="html"><![CDATA[${post.title}]]></title>
    <link rel="alternate" type="text/html" href="${post.permalink}" />
    <id>${post.permalink}</id>
    <updated>${post.updated.strftime("%Y-%m-%dT%H:%M:%SZ")}</updated>
    <published>${post.date.strftime("%Y-%m-%dT%H:%M:%SZ")}</published>
% for category in post.categories:
    <category scheme="${config.blog_url}" term="${category}" />
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

__post_mako = """<%page args="post"/>
<div class="blog_post">
  <a name="${post.title}" />
  <h2 class="blog_post_title"><a href="${post.permapath()}" rel="bookmark" title="Permanent Link to ${post.title}">${post.title}</a></h2>
  <small>${post.date.strftime("%B %-d, %Y at %-I:%M %p")} | categories: 
<% 
   category_links = []
   for category in post.categories:
       if post.draft:
           #For drafts, we don't write to the category dirs, so just write the categories as text
           category_links.append(category)
       else:
           category_links.append("<a href='/category/%s'>%s</a>" % (category_link_names[category], category))
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
 This is the index page's content.
</p>
"""

__post_1 = """
---
categories: Category 1
date: 2009/07/23 15:22:00
format: markdown
permalink: http://www.your-full-site-url.com/2009/07/23/post-one
title: Post 1
---
This is post #1"""

__post_2 = """
---
categories: Category 2
date: 2009/07/23 15:22:00
format: markdown
permalink: http://www.your-full-site-url.com/2009/07/23/post-two
title: Post 2
---
This is post #2"""

def do_init(options):
    if len(os.listdir(options.config_dir)) > 0 :
        print("This directory is not empty, will not attempt to initialize here : %s" % format(options.config_dir))
        return
    print("Building a minimal blogofile site at : %s" % format(options.config_dir))
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
    t = open(os.path.join("_templates","rss.mako"),"w")
    t.write(__rss_mako)
    t.close()
    t = open(os.path.join("_templates","atom.mako"),"w")
    t.write(__atom_mako)
    t.close()
    t = open(os.path.join("_templates","permapage.mako"),"w")
    t.write(__permapage_mako)
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
    print("This is a stub, this isn't complete yet.")
