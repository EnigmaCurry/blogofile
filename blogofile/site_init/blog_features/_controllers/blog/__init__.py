import logging
from mako.lookup import TemplateLookup

from blogofile.cache import bf

import archives
import categories
import chronological
import feed
import permapage
import post

config = {
        "name": "Blog",
        "description": "Creates a Blog",
        "version": "@BLOGOFILE_VERSION_REPLACED_HERE@",
        "priority": 90.0,
        "template_path": "_templates/blog",
        "base_template": "site.mako",

        #Posts
        "post.date_format": "%Y/%m/%d %H:%M:%S"
        }

template_lookup = None #instantiate in init

def materialize_template(template_name, location, attrs={}, lookup=None):
    #Just like the regular bf.writer.materialize_template.
    #However, this uses the blog template lookup by default.
    if lookup==None:
        lookup = template_lookup
    bf.writer.materialize_template(template_name, location, attrs, lookup)
    
def init():
    global template_lookup
    template_lookup = TemplateLookup(
        directories=[config["template_path"],"_templates"],
        input_encoding='utf-8', output_encoding='utf-8',
        encoding_errors='replace')
    base_template = template_lookup.get_template(config["base_template"])
    template_lookup.put_template("blog_base_template",base_template)

def run():
    blog = bf.config.controllers.blog

    #Parse the posts
    blog.posts = post.parse_posts("_posts")
    blog.dir = bf.util.path_join(bf.writer.output_dir, blog.path)

    # Find all the categories and archives before we write any pages
    blog.archived_posts = {} ## "/archive/Year/Month" -> [post, post, ... ]
    blog.archive_links = []  ## [("/archive/2009/12", name, num_in_archive1), ...] (sorted in reverse by date)
    blog.categorized_posts = {} ## "Category Name" -> [post, post, ... ]
    blog.all_categories = [] ## [("Category 1",num_in_category_1), ...] (sorted alphabetically)
    archives.sort_into_archives()
    categories.sort_into_categories()

    blog.logger = logging.getLogger(config['name'])
    
    permapage.run()
    chronological.run()
    archives.run()
    categories.run()
    feed.run()

