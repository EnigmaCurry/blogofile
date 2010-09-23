import urlparse
from blogofile.cache import bf
import re

blog = bf.config.controllers.blog


def run():
    write_permapages()


def write_permapages():
    "Write blog posts to their permalink locations"
    site_re = re.compile(bf.config.site.url, re.IGNORECASE)
    for post in blog.posts:
        if post.permalink:
            path = site_re.sub("", post.permalink)
            blog.logger.info("Writing permapage for post: {0}".format(path))
        else:
            #Permalinks MUST be specified. No permalink, no page.
            blog.logger.info("Post has no permalink: {0}".format(post.title))
            continue
        try:
            bf.util.mkdir(path)
        except OSError:
            pass

        env = {
            "post": post,
            "posts": blog.posts
        }

        #Find the next and previous posts chronologically
        for post_num in range(0,len(blog.posts)):
            if blog.posts[post_num] == post:
                if post_num < len(blog.posts) - 1:
                    env['prev_post'] = blog.posts[post_num + 1]
                if post_num > 0:
                    env['next_post'] = blog.posts[post_num - 1]
                break
        bf.writer.materialize_template(
                "permapage.mako", bf.util.path_join(path,"index.html"), env)
