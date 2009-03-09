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

class Writer:
    def __init__(self, output_dir, config):
        #Base templates are templates (usually in ./_templates) that are only
        #referenced by other templates.
        self.base_template_dir = os.path.join(".","_templates")
        self.output_dir        = output_dir
        self.template_lookup = TemplateLookup(
            directories=[".", self.base_template_dir],
            input_encoding='utf-8', output_encoding='utf-8',
            encoding_errors='replace')
        self.config=config

        #Behavioural settings:
        self.do_prettify = eval(config.get("blogofile","pretty_html"))
        #Kodos, you rule (http://kodos.sourceforge.net/):
        self.files_exclude_regex = re.compile("(^_.*)|(^#.*)|(^.*~$)")
        self.dirs_exclude_regex = re.compile("(^\.git)|(^\.hg)|(^\.bzr)|(^\.svn)|(^\CVS)")
        
    def write_blog(self, posts, drafts=None):
        self.archive_links = self.__get_archive_links(posts)
        self.all_categories = self.__get_all_categories(posts)
        self.category_link_names = self.__compute_category_link_names(self.all_categories)
        self.__setup_output_dir()
        self.__write_files(posts)
        self.__write_blog_chron(posts)
        self.__write_permapage(posts)
        if drafts:
            self.__write_permapage(drafts)
        self.__write_monthly_archives(posts)
        self.__write_blog_categories(posts)
        self.__write_feed(posts, "/feed", "rss.mako")
        self.__write_feed(posts, "/feed/atom", "atom.mako")

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
        xml = feed_template.render(posts=posts,config=self.config)
        try:
            os.makedirs(os.path.join(self.output_dir,root))
        except OSError:
            pass
        f = open(os.path.join(self.output_dir,root,"index.xml"),"w")
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
        # Clear out the old staging directory.  I *would* just shutil.rmtree the
        # whole thing and recreate it, but I want the output_dir to retain it's
        # same inode on the filesystem to be compatible with some HTTP servers. So
        # this just deletes the *contents* of output_dir
        try:
            os.makedirs(self.output_dir)
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
                if d.startswith("_"):
                    dirs.remove(d)
                if self.dirs_exclude_regex.match(d):
                    dirs.remove(d)
            try:
                os.makedirs(os.path.join(self.output_dir, root))
            except OSError:
                pass
            for t_fn in files:
                if self.files_exclude_regex.match(t_fn):
                    #Ignore this file.
                    continue
                elif t_fn.endswith(".mako"):
                    #Process this template file
                    t_name = t_fn[:-5]
                    t_file = open(os.path.join(root, t_fn))
                    template = Template(t_file.read(), output_encoding="utf-8",
                                        lookup=self.template_lookup)
                    t_file.close()
                    path = os.path.join(self.output_dir,root,t_name)
                    html_file = open(path,"w")
                    html = template.render(posts=posts,
                                           config=self.config,
                                           archive_links=self.archive_links,
                                           all_categories=self.all_categories,
                                           category_link_names=self.category_link_names)
                    #Prettyify the html
                    if self.do_prettify:
                        soup = BeautifulSoup.BeautifulSoup(html)
                        html = soup.prettify()
                    #Write to disk
                    html_file.write(html)
                else:
                    #Copy this non-template file
                    f_path = os.path.join(root, t_fn)
                    shutil.copyfile(f_path,os.path.join(self.output_dir,f_path))

    def __write_blog_chron(self, posts, num_per_page=5, root="/page"):
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
            page_posts = posts[post_num:post_num+num_per_page]
            post_num += num_per_page
            if page_num > 1:
                prev_link = "../" + str(page_num - 1)
            else:
                prev_link = None
            if len(posts) > post_num:
                next_link = "../" + str(page_num + 1)
            else:
                next_link = None
            page_dir = os.path.join(self.output_dir,root,str(page_num))
            os.makedirs(page_dir)
            fn = os.path.join(page_dir,"index.html")
            f = open(fn,"w")
            html = chron_template.render(posts=page_posts,
                                         next_link=next_link,
                                         prev_link=prev_link,
                                         config=self.config,
                                         archive_links=self.archive_links,
                                         all_categories=self.all_categories,
                                         category_link_names=self.category_link_names)
            #Prettify html
            if self.do_prettify:
                soup = BeautifulSoup.BeautifulSoup(html)
                html = soup.prettify()
            f.write(html)
            f.close()
            page_num += 1
        

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
                path = os.path.join(self.output_dir,
                                    urlparse.urlparse(post.permalink)[2].lstrip("/"))
            else:
                #Permalinks MUST be specified. No permalink, no page.
                continue
            try:
                os.makedirs(path)
            except OSError:
                pass
            html = perma_template.render(post=post,
                                         posts=posts,
                                         config=self.config,
                                         archive_links=self.archive_links,
                                         all_categories=self.all_categories,
                                         category_link_names=self.category_link_names)
            #Prettify html
            if self.do_prettify:
                soup = BeautifulSoup.BeautifulSoup(html)
                html = soup.prettify()
            f = open(os.path.join(path,"index.html"), "w")
            f.write(html)
            f.close()

    def __write_blog_categories(self, posts, root="/category", posts_per_page=5):
        """Write all the blog posts in categories"""
        #TODO: Paginate this.
        root = root.lstrip("/")
        chron_template = self.template_lookup.get_template("chronological.mako")
        chron_template.output_encoding = "utf-8"
        #Find all the categories:
        categories = set()
        for post in posts:
            categories.update(post.categories)
        for category in categories:
            category_posts = [post for post in posts if category in post.categories]
            category_link_name = self.category_link_names[category]
            #Write category RSS feed
            self.__write_feed(category_posts,os.path.join(
                    root,category_link_name,"feed"),"rss.mako")
            self.__write_feed(category_posts,os.path.join(
                    root,category_link_name,"feed","atom"),"atom.mako")
            page_num = 1
            while True:
                path = os.path.join(self.output_dir,root,category_link_name,str(page_num),"index.html")
                try:
                    os.makedirs(os.path.split(path)[0])
                except OSError:
                    pass
                f = open(path, "w")
                page_posts = category_posts[:posts_per_page]
                category_posts = category_posts[posts_per_page:]
                #Forward and back links
                if page_num > 1:
                    prev_link = "/%s/%s/%s" % (root, category_link_name, str(page_num - 1))
                else:
                    prev_link = None
                if len(category_posts) > 0:
                    next_link = "/%s/%s/%s" % (root, category_link_name, str(page_num + 1))
                else:
                    next_link = None
                html = chron_template.render(posts=page_posts,
                                             prev_link=prev_link,
                                             next_link=next_link,
                                             config=self.config,
                                             archive_links=self.archive_links,
                                             all_categories=self.all_categories,
                                             category_link_names=self.category_link_names)
                #Prettify html
                if self.do_prettify:
                    soup = BeautifulSoup.BeautifulSoup(html)
                    html = soup.prettify()
                f.write(html)
                f.close()
                #Copy category/1 to category/index.html
                if page_num == 1:
                    shutil.copyfile(path,os.path.join(
                            self.output_dir,root,category_link_name,"index.html"))
                #Prepare next iteration
                page_num += 1
                if len(category_posts) == 0:
                    break

