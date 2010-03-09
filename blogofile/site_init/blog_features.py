#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Blog features common to most blog types"""

__author__ = "Ryan McGuire (ryan@enigmacurry.com)"

import os
from .. import config

atom_mako = """<?xml version="1.0" encoding="UTF-8"?><% from datetime import datetime %>
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
    <category scheme="${bf.config.blog_url}" term="${category}" />
% endfor
    <summary type="html"><![CDATA[${post.title}]]></summary>
    <content type="html" xml:base="${post.permalink}"><![CDATA[${post.content}]]></content>
  </entry>
% endfor
</feed>
"""

base_mako = """<%def name="filter(chain)">
  ${bf.filter.run_chain(chain, capture(caller.body))}
</%def>

${next.body()}
"""

chronological_mako = """<%inherit file="site.mako" />
% for post in posts:
  <%include file="post.mako" args="post=post" />
% if bf.config.disqus_enabled:
  <div class="after_post"><a href="${post.permalink}#disqus_thread">Read and Post Comments</a></div>
% endif
  <hr class="interblog" />
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

footer_mako = """
<p id="credits">
Powered by <a href="http://www.blogofile.com">Blogofile</a>.<br/>
<br/>
RSS feeds for <a href="${bf.config.util.site_path_helper(bf.config.blog_path,'feed')}">Entries</a>
% if bf.config.disqus_enabled:
 and <a
href="http://${bf.config.disqus_name}.disqus.com/latest.rss">Comments</a>.
% endif
<br>
</p>
% if bf.config.disqus_enabled:
<script type="text/javascript">
//<![CDATA[
(function() {
		var links = document.getElementsByTagName('a');
		var query = '?';
		for(var i = 0; i < links.length; i++) {
			if(links[i].href.indexOf('#disqus_thread') >= 0) {
				query += 'url' + i + '=' + encodeURIComponent(links[i].href) + '&';
			}
		}
		document.write('<script charset="utf-8" type="text/javascript" src="http://disqus.com/forums/${bf.config.disqus_name}/get_num_replies.js' + query + '"></' + 'script>');
	})();
//]]>
</script>
% endif
"""

head_mako = """<title>${bf.config.blog_name}</title>
<link rel="alternate" type="application/rss+xml" title="RSS 2.0" href="${bf.util.site_path_helper(bf.config.blog_path,'/feed')}" />
<link rel="alternate" type="application/atom+xml" title="Atom 1.0" href="${bf.util.site_path_helper(bf.config.blog_path,'/feed/atom')}" />
"""

permapage_mako = """<%inherit file="site.mako" />
<%include file="post.mako" args="post=post" />
<div id="disqus_thread"></div>
<script type="text/javascript">
  var disqus_url = "${post.permalink}";
</script>
% if bf.config.disqus_enabled:
<script type="text/javascript" src="http://disqus.com/forums/${bf.config.disqus_name}/embed.js"></script>
<noscript><a href="http://${bf.config.disqus_name}.disqus.com/?url=ref">View the discussion thread.</a></noscript><a href="http://disqus.com" class="dsq-brlink">blog comments powered by <span class="logo-disqus">Disqus</span></a>
% endif
"""

post_excerpt_mako = """<%inherit file="post.mako" />
<%def name="post_prose(post)">
  ${post.excerpt}
</%def>
"""

post_mako = """<%page args="post"/>
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
           category_links.append("<a href='%s'>%s</a>" % (category.path, category.name))
%>
${", ".join(category_links)}
% if bf.config.disqus_enabled:
 | <a href="${post.permalink}#disqus_thread">View Comments</a>
% endif
</small><p/>
  <span class="post_prose">
    ${self.post_prose(post)}
  </span>
</div>

<%def name="post_prose(post)">
  ${post.content}
</%def>
"""

rss_mako = """<?xml version="1.0" encoding="UTF-8"?><% from datetime import datetime %>
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

initial_py = """\"\"\"Initialize some things before rendering\"\"\"

from blogofile.cache import bf

bf.all_categories = []
bf.archive_links = []
"""

archives_py = """from blogofile.cache import bf

def run():
    write_monthly_archives(bf.posts)

def write_monthly_archives(posts):
    m = {} # "/archive/%Y/%m" -> [post, post, ... ]
    for post in posts:
        link = post.date.strftime("/archive/%Y/%m")
        try:
            m[link].append(post)
        except KeyError:
            m[link] = [post]
    for link, posts in m.items():
        name = posts[0].date.strftime("%B %Y")
        bf.controllers.chronological.write_blog_chron(posts,root=link)
        bf.archive_links.append((bf.config.blog_path+link,name,len(posts)))
"""

categories_py = """import os
import shutil
from blogofile.cache import bf

def run():
    write_categories()

def write_categories():
    \"\"\"Write all the blog posts in categories\"\"\"
    root = bf.util.path_join(bf.config.blog_path,bf.config.blog_category_dir)
    #Find all the categories:
    categories = set()
    for post in bf.posts:
        categories.update(post.categories)
    for category in categories:
        category_posts = [post for post in bf.posts \
                              if category in post.categories]
        #Update the categories sidebar models
        bf.all_categories.append((category,len(category_posts)))
        #Write category RSS feed
        bf.controllers.feed.write_feed(category_posts,bf.util.path_join(
                bf.config.blog_path, bf.config.blog_category_dir,
                category.url_name,"feed"),"rss.mako")
        bf.controllers.feed.write_feed(category_posts,bf.util.path_join(
                bf.config.blog_path, bf.config.blog_category_dir,
                category.url_name,"feed","atom"),"atom.mako")
        page_num = 1
        while True:
            path = bf.util.path_join(root,category.url_name,
                                str(page_num),"index.html")
            page_posts = category_posts[:bf.config.blog_posts_per_page]
            category_posts = category_posts[bf.config.blog_posts_per_page:]
            #Forward and back links
            if page_num > 1:
                prev_link = bf.util.path_join(
                    bf.config.blog_path, bf.config.blog_category_dir, category.url_name,
                                           str(page_num - 1))
            else:
                prev_link = None
            if len(category_posts) > 0:
                next_link = bf.util.path_join(
                    bf.config.blog_path, bf.config.blog_category_dir, category.url_name,
                                           str(page_num + 1))
            else:
                next_link = None
            bf.writer.materialize_template("chronological.mako", path, {
                    "posts": page_posts,
                    "prev_link": prev_link,
                    "next_link": next_link })
            #Copy category/1 to category/index.html
            if page_num == 1:
                shutil.copyfile(bf.util.path_join(bf.writer.output_dir,path),bf.util.path_join(
                        bf.writer.output_dir,root,category.url_name,
                        "index.html"))
            #Prepare next iteration
            page_num += 1
            if len(category_posts) == 0:
                break

"""

chronological_py = """# Write all the blog posts in reverse chronological order
import os
from blogofile.cache import bf

def run():
    write_blog_chron(posts=bf.posts,
                     root=bf.config.blog_pagination_dir.lstrip("/"))
    write_blog_first_page()

def write_blog_chron(posts,root):
    page_num = 1
    post_num = 0
    html = []
    while len(posts) > post_num:
        #Write the pages, num_per_page posts per page:
        page_posts = posts[post_num:post_num+bf.config.blog_posts_per_page]
        post_num += bf.config.blog_posts_per_page
        if page_num > 1:
            prev_link = "../" + str(page_num - 1)
        else:
            prev_link = None
        if len(posts) > post_num:
            next_link = "../" + str(page_num + 1)
        else:
            next_link = None
        page_dir = bf.util.path_join(bf.config.blog_path,root,str(page_num))
        fn = bf.util.path_join(page_dir,"index.html")
        bf.writer.materialize_template("chronological.mako", fn,
            { "posts":page_posts,
              "next_link":next_link,
              "prev_link":prev_link })
        page_num += 1
        
def write_blog_first_page():
    if not bf.config.blog_custom_index:
        page_posts = bf.posts[:bf.config.blog_posts_per_page]
        path = bf.util.path_join(bf.config.blog_path,"index.html")
        bf.logger.info("Writing blog index page: "+path)
        if len(bf.posts) > bf.config.blog_posts_per_page:
            next_link = bf.util.site_path_helper(bf.config.blog_path,bf.config.blog_pagination_dir+"/2")
        else:
            next_link = None
        bf.writer.materialize_template("chronological.mako", path,
            { "posts": page_posts,
              "next_link": next_link,
              "prev_link": None })
"""

feed_py = """from blogofile.cache import bf

def run():
    write_feed(bf.posts, bf.util.path_join(bf.config.blog_path,"feed"), "rss.mako")
    write_feed(bf.posts, bf.util.path_join(bf.config.blog_path,"feed","atom"),
                          "atom.mako")

def write_feed(posts, root, template):
    root = root.lstrip("/")
    path = bf.util.path_join(root,"index.xml")
    bf.logger.info("Writing RSS/Atom feed: "+path)
    bf.writer.materialize_template(template, path, {"posts":posts, "root":root})
"""
permapage_py = """import urlparse
from blogofile.cache import bf
import re

def run():
    write_permapages()

def write_permapages():
    "Write blog posts to their permalink locations"
    site_re = re.compile(bf.config.site_url, re.IGNORECASE)
    for post in bf.posts:
        if post.permalink:
            path = site_re.sub("",post.permalink)
            bf.logger.info("Writing permapage for post: "+path)
        else:
            #Permalinks MUST be specified. No permalink, no page.
            bf.logger.info("Post has no permalink: "+post.title)
            continue
        try:
            bf.util.mkdir(path)
        except OSError:
            pass
        bf.writer.materialize_template(
            "permapage.mako", bf.util.path_join(path,"index.html"), 
            { "post": post, "posts": bf.posts })
        
"""

markdown_py = """import markdown
import logging

#Markdown logging is noisy, pot it down:
logging.getLogger("MARKDOWN").setLevel(logging.ERROR)

def run(content):
    return markdown.markdown(content)
"""

textile_py = """import textile

def run(content):
    return textile.textile(content)
"""

syntax_highlight_py = """def run(content):
    return content
"""
