import os
import shutil
import operator
import feed
from blogofile.cache import bf

blog = bf.config.controllers.blog


def run():
    write_categories()


def sort_into_categories():
    categories = set()
    for post in blog.posts:
        categories.update(post.categories)
    for category in categories:
        category_posts = [post for post in blog.posts
                            if category in post.categories]
        blog.categorized_posts[category] = category_posts
    for category, posts in sorted(
        blog.categorized_posts.items(), key=operator.itemgetter(0)):
        blog.all_categories.append((category, len(posts)))


def write_categories():
    """Write all the blog posts in categories"""
    root = bf.util.path_join(blog.path, blog.category_dir)
    #Find all the categories:
    categories = set()
    for post in blog.posts:
        categories.update(post.categories)
    for category, category_posts in blog.categorized_posts.items():
        #Write category RSS feed
        rss_path = bf.util.fs_site_path_helper(
            blog.path, blog.category_dir,
            category.url_name, "feed")
        feed.write_feed(category_posts,rss_path, "rss.mako")
        atom_path = bf.util.fs_site_path_helper(
            blog.path, blog.category_dir,
            category.url_name, "feed", "atom")
        feed.write_feed(category_posts, atom_path, "atom.mako")
        page_num = 1
        while True:
            path = bf.util.path_join(root, category.url_name,
                                str(page_num), "index.html")
            page_posts = category_posts[:blog.posts_per_page]
            category_posts = category_posts[blog.posts_per_page:]
            #Forward and back links
            if page_num > 1:
                prev_link = bf.util.site_path_helper(
                    blog.path, blog.category_dir, category.url_name,
                                           str(page_num - 1))
            else:
                prev_link = None
            if len(category_posts) > 0:
                next_link = bf.util.site_path_helper(
                    blog.path, blog.category_dir, category.url_name,
                                           str(page_num + 1))
            else:
                next_link = None
            
            env = {
                "category": category,
                "posts": page_posts,
                "prev_link": prev_link,
                "next_link": next_link
            }
            bf.writer.materialize_template("chronological.mako", path, env)
            
            #Copy category/1 to category/index.html
            if page_num == 1:
                shutil.copyfile(
                        bf.util.path_join(bf.writer.output_dir, path),
                        bf.util.path_join(
                                bf.writer.output_dir, root, category.url_name,
                                "index.html"))
            #Prepare next iteration
            page_num += 1
            if len(category_posts) == 0:
                break
