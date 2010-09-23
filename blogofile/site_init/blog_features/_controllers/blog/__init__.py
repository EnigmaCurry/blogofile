import logging

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
        "priority": 90.0,

        #Posts
        "post.date_format": "%Y/%m/%d %H:%M:%S"
        }

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

