import urlparse
from blogofile.cache import bf
import re

blog = bf.config.controllers.blog


def run():
    write_permapages()


def write_permapages():
    "Write blog posts to their permalink locations"
    site_re = re.compile(bf.config.site.url, re.IGNORECASE)
    num_posts = len(blog.posts)
    
    for i, post in enumerate(blog.posts):
        if post.permalink:
            path = site_re.sub("", post.permalink)
            blog.logger.info(u"Writing permapage for post: {0}".format(path))
        else:
            #Permalinks MUST be specified. No permalink, no page.
            blog.logger.info(u"Post has no permalink: {0}".format(post.title))
            continue

        env = {
            "post": post,
            "posts": blog.posts
        }

        #Find the next and previous posts chronologically
        if i < num_posts - 1:
            env['prev_post'] = blog.posts[i + 1]
        if i > 0:
            env['next_post'] = blog.posts[i - 1]
        
        bf.writer.materialize_template(
                "permapage.mako", bf.util.path_join(path, "index.html"), env)
