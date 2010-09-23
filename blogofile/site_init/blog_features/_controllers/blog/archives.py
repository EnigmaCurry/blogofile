################################################################################
## Archives controller
##
## Writes out yearly, monthly, and daily archives.
## Each archive is navigable to the next and previous archive
## in which posts were made.
################################################################################

import operator

from blogofile.cache import bf
import chronological

blog = bf.config.controllers.blog


def run():
    write_monthly_archives()


def sort_into_archives():
    #This is run in 0.initial.py
    for post in blog.posts:
        link = post.date.strftime("archive/%Y/%m")
        try:
            blog.archived_posts[link].append(post)
        except KeyError:
            blog.archived_posts[link] = [post]
    for archive, posts in sorted(
        blog.archived_posts.items(), key=operator.itemgetter(0), reverse=True):
        name = posts[0].date.strftime("%B %Y")
        blog.archive_links.append((archive, name, len(posts)))


def write_monthly_archives():
    for link, posts in blog.archived_posts.items():
        name = posts[0].date.strftime("%B %Y")
        chronological.write_blog_chron(posts, root=link)
