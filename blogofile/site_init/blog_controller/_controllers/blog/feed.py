from blogofile.cache import bf

blog = bf.config.controllers.blog


def run():
    feed_posts = list(blog.iter_posts_published(limit=10))
    write_feed(feed_posts, bf.util.path_join(blog.path, "feed"), "rss.mako")
    write_feed(feed_posts, bf.util.path_join(blog.path, "feed", "atom"),
                          "atom.mako")

def write_feed(posts, root, template):
    root = root.lstrip("/")
    path = bf.util.path_join(root, "index.xml")
    blog.logger.info("Writing RSS/Atom feed: " + path)
    env = {"posts": posts, "root": root}
    blog.mod.materialize_template(template, path, env)
