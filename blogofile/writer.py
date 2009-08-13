#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
writer.py writes out the static blog to ./_site based on templates found in the
current working directory.
"""

__author__ = "Ryan McGuire (ryan@enigmacurry.com)"
__date__   = "Tue Feb  3 12:50:17 2009"

import os
import shutil
import urlparse
import re
import operator

from mako.template import Template
from mako.lookup import TemplateLookup
import BeautifulSoup

from main import logger
import util
import config

class Writer:
    def __init__(self, output_dir):
        #Base templates are templates (usually in ./_templates) that are only
        #referenced by other templates.
        self.base_template_dir = os.path.join(".","_templates")
        self.output_dir        = output_dir
        self.blog_dir          = util.get_blog_dir(output_dir)
        self.template_lookup = TemplateLookup(
            directories=[".", self.base_template_dir],
            input_encoding='utf-8', output_encoding='utf-8',
            encoding_errors='replace')

    def write_blog(self, posts, drafts=None):
        self.archive_links = self.__get_archive_links(posts)
        self.all_categories = self.__get_all_categories(posts)
        self.category_link_names = self.__compute_category_link_names(
            self.all_categories)
        self.__setup_output_dir()
        self.__write_files(posts)
        self.__write_blog_chron(posts, root=config.blog_pagination_dir)
        self.__write_blog_first_page(posts)
        self.__write_permapage(posts)
        if drafts:
            self.__write_permapage(drafts)
        self.__write_monthly_archives(posts)
        self.__write_blog_categories(posts)
        self.__write_feed(posts, "feed", "rss.mako")
        self.__write_feed(posts, "feed/atom", "atom.mako")
        self.__write_pygments_css()
        
    def __get_archive_links(self, posts):
        """Return a list of monthly archive links and nice name:
        """
        d = {} #(link, name) -> number that month
        for post in posts:
            link = post.date.strftime("/%Y/%m/1")
            name = post.date.strftime("%B %Y")
            try:
                d[(link, name)] += 1
            except KeyError:
                d[(link, name)] = 1
        l = [key+(value,) for key, value in d.items()]
        l = sorted(l, key=operator.itemgetter(0), reverse=True)
        return l

    def __get_all_categories(self, posts):
        """Return a list of all the categories of all posts"""
        d = {} #category -> number of posts
        for post in posts:
            for category in post.categories:
                try:
                    d[category] += 1
                except KeyError:
                    d[category] = 1
        l = sorted(d.items(), key=operator.itemgetter(0))
        return l

    def __write_feed(self, posts, root, template):
        root = root.lstrip("/")
        feed_template = self.template_lookup.get_template(template)
        feed_template.output_encoding = "utf-8"
        xml = feed_template.render(posts=posts,root=root,config=config)
        try:
            util.mkdir(os.path.join(self.blog_dir,root))
        except OSError:
            pass
        f = open(os.path.join(self.blog_dir,root,"index.xml"),"w")
        f.write(xml)
        f.close()
    
    def __compute_category_link_names(self, categories):
        """Transform category names into URL friendly names

        example: "Cool Stuff" -> "cool-stuff"     """
        d = {} #name->nice_name
        for category, n in categories:
            nice_name = category.lower().replace(" ","-")
            d[category] = nice_name
        return d
    
    def __setup_output_dir(self):
        # Clear out the old staging directory.  I *would* just shutil.rmtree
        # the whole thing and recreate it, but I want the output_dir to
        # retain it's same inode on the filesystem to be compatible with some
        # HTTP servers. So this just deletes the *contents* of output_dir
        try:
            util.mkdir(self.output_dir)
        except OSError:
            pass
        for f in os.listdir(self.output_dir):
            f = os.path.join(self.output_dir,f)
            try:
                os.remove(f)
            except OSError:
                pass
            try:
                shutil.rmtree(f)
            except OSError:
                pass
            
    def __write_files(self, posts):
        """Write all files for the blog to _site

        Convert all templates to straight HTML
        Copy other non-template files directly"""
        #find mako templates in template_dir
        for root, dirs, files in os.walk("."):
            excluded_roots = []
            if root.startswith("./"):
                root = root[2:]
            for d in list(dirs):
                #Exclude some dirs
                d_path = os.path.join(root,d)
                if util.should_ignore_path(d_path):
                    logger.info("Ignoring directory : "+d_path)
                    dirs.remove(d)
            try:
                util.mkdir(os.path.join(self.output_dir, root))
            except OSError:
                pass
            for t_fn in files:
                t_fn_path = os.path.join(root,t_fn)
                if util.should_ignore_path(t_fn_path):
                    #Ignore this file.
                    logger.info("Ignoring file : "+t_fn_path)
                    continue
                elif t_fn.endswith(".mako"):
                    logger.info("Processing mako file: "+t_fn_path)
                    #Process this template file
                    t_name = t_fn[:-5]
                    t_file = open(t_fn_path)
                    template = Template(t_file.read().decode("utf-8"), output_encoding="utf-8",
                                        lookup=self.template_lookup)
                    t_file.close()
                    path = os.path.join(self.output_dir,root,t_name)
                    html_file = open(path,"w")
                    html = template.render(
                        posts=posts,
                        config=config,
                        archive_links=self.archive_links,
                        all_categories=self.all_categories,
                        category_link_names=self.category_link_names)
                    #Syntax highlighting
                    if config.syntax_highlight_enabled:
                        html = util.do_syntax_highlight(html,config)
                    #Write to disk
                    html_file.write(html)
                else:
                    #Copy this non-template file
                    f_path = os.path.join(root, t_fn)
                    logger.info("Copying file : "+f_path)
                    shutil.copyfile(f_path,os.path.join(self.output_dir,f_path))

    def __write_blog_chron(self, posts, root="page"):
        """Write all the blog posts in reverse chronological order

        Writes the first num_per_page posts to /root/1
        Writes the second num_per_page posts to /root/2 etc
        """
        root = root.lstrip("/")
        chron_template = self.template_lookup.get_template("chronological.mako")
        chron_template.output_encoding = "utf-8"
        page_num = 1
        post_num = 0
        html = []
        while len(posts) > post_num:
            #Write the pages, num_per_page posts per page:
            page_posts = posts[post_num:post_num+config.blog_posts_per_page]
            post_num += config.blog_posts_per_page
            if page_num > 1:
                prev_link = "../" + str(page_num - 1)
            else:
                prev_link = None
            if len(posts) > post_num:
                next_link = "../" + str(page_num + 1)
            else:
                next_link = None
            page_dir = os.path.join(self.blog_dir,root,str(page_num))
            util.mkdir(page_dir)
            fn = os.path.join(page_dir,"index.html")
            f = open(fn,"w")
            html = chron_template.render(
                posts=page_posts,
                next_link=next_link,
                prev_link=prev_link,
                config=config,
                archive_links=self.archive_links,
                all_categories=self.all_categories,
                category_link_names=self.category_link_names)
            f.write(html)
            f.close()
            page_num += 1
        
    def __write_blog_first_page(self, posts):
        if not config.blog_custom_index:
            chron_template = self.template_lookup.get_template("chronological.mako")
            chron_template.output_encoding = "utf-8"
            page_posts = posts[:config.blog_posts_per_page]
            path = os.path.join(self.blog_dir,"index.html")
            logger.info("Writing blog index page: "+path)
            f = open(path,"w")
            if len(posts) > config.blog_posts_per_page:
                next_link = os.path.join(
                    config.blog_path,config.blog_pagination_dir,"2")
            else:
                next_link = None
            html = chron_template.render(
                posts=page_posts,
                next_link=next_link,
                prev_link=None,
                config=config,
                archive_links=self.archive_links,
                all_categories=self.all_categories,
                category_link_names=self.category_link_names)
            f.write(html)
            f.close()          

    def __write_monthly_archives(self, posts):
        m = {} # "/%Y/%m" -> [post, post, ... ]
        for post in posts:
            link = post.date.strftime("/%Y/%m")
            try:
                m[link].append(post)
            except KeyError:
                m[link] = [post]
        for link, posts in m.items():
            self.__write_blog_chron(posts,root=link)

    def __write_permapage(self, posts):
        """Write blog posts to their permalink locations"""
        perma_template = self.template_lookup.get_template("permapage.mako")
        perma_template.output_encoding = "utf-8"
        for post in posts:
            if post.permalink:
                path = os.path.join(
                    self.output_dir, urlparse.urlparse(
                        post.permalink)[2].lstrip("/"))
            else:
                #Permalinks MUST be specified. No permalink, no page.
                logger.info("Post has no permalink: "+post.title)
                continue
            try:
                util.mkdir(path)
            except OSError:
                pass
            html = perma_template.render(
                post=post,
                posts=posts,
                config=config,
                archive_links=self.archive_links,
                all_categories=self.all_categories,
                category_link_names=self.category_link_names)
            f = open(os.path.join(path,"index.html"), "w")
            logger.info("Writing permapage for post: "+path)
            f.write(html)
            f.close()

    def __write_pygments_css(self):
        css_dir = os.path.join(self.output_dir, "css")
        try:
            util.mkdir(css_dir)
        except OSError:
            pass
        if config.syntax_highlight_enabled:
            f = open(os.path.join(css_dir,"pygments.css"),"w")
            f.write(config.html_formatter.get_style_defs(".highlight"))
            f.close()

    def __write_blog_categories(self, posts,
                                posts_per_page=5):
        """Write all the blog posts in categories"""
        root = os.path.join(self.blog_dir,config.blog_category_dir)
        chron_template = self.template_lookup.get_template("chronological.mako")
        chron_template.output_encoding = "utf-8"
        #Find all the categories:
        categories = set()
        for post in posts:
            categories.update(post.categories)
        for category in categories:
            category_posts = [post for post in posts \
                                  if category in post.categories]
            category_link_name = self.category_link_names[category]
            #Write category RSS feed
            self.__write_feed(category_posts,os.path.join(
                    root,category_link_name,"feed"),"rss.mako")
            self.__write_feed(category_posts,os.path.join(
                    root,category_link_name,"feed","atom"),"atom.mako")
            page_num = 1
            while True:
                path = os.path.join(root,category_link_name,
                                    str(page_num),"index.html")
                try:
                    util.mkdir(os.path.split(path)[0])
                except OSError:
                    pass
                f = open(path, "w")
                page_posts = category_posts[:posts_per_page]
                category_posts = category_posts[posts_per_page:]
                #Forward and back links
                if page_num > 1:
                    prev_link = os.path.join(
                        config.blog_path, config.blog_category_dir, category_link_name,
                                               str(page_num - 1))
                    logger.info("Prev link: "+prev_link)
                else:
                    prev_link = None
                if len(category_posts) > 0:
                    next_link = os.path.join(
                        config.blog_path, config.blog_category_dir, category_link_name,
                                               str(page_num + 1))
                    logger.info("Next link: "+next_link)
                else:
                    next_link = None
                html = chron_template.render(
                    posts=page_posts,
                    prev_link=prev_link,
                    next_link=next_link,
                    config=config,
                    archive_links=self.archive_links,
                    all_categories=self.all_categories,
                    category_link_names=self.category_link_names)
                f.write(html)
                f.close()
                #Copy category/1 to category/index.html
                if page_num == 1:
                    shutil.copyfile(path,os.path.join(
                            root,category_link_name,
                            "index.html"))
                #Prepare next iteration
                page_num += 1
                if len(category_posts) == 0:
                    break

