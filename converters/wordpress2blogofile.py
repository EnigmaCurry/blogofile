#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Export a Wordpress blog to Blogofile /_posts directory format

This file is a part of Blogofile (http://www.blogofile.com)

This file is MIT licensed, see http://blogofile.com/LICENSE.html for details.

Requirements:

  * An existing Wordpress database hosted on MySQL (other databases probably work
    too, you just need to craft your own db_conn string below.)

  * python-mysqldb (http://mysql-python.sourceforge.net/)
    On Ubuntu this is easy to get: sudo apt-get install python-mysqldb

  * Configure the connection details below and run:

    python wordpress2blogofile.py

    If everything worked right, this will create a _posts directory with your converted posts.
"""

import os
import re
import sys
import yaml
import codecs
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declarative_base

#########################
## Config
#########################
table_prefix = "wp_"

#MySQL config options.
#   (Other databases probably supported, but untested. Just craft your own
#    db_conn string according to the SQLAlchemy docs. See : http://is.gd/M1vU6j )
db_username  = "your_database_username"
db_password  = "your_database_password"
db_host      = "127.0.0.1"
db_port      = "3306"
db_database  = "name_of_wordpress_database"
db_encoding  = "utf8"
db_conn      = "mysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_database}?charset={db_encoding}".format(**locals())

# End Config
#########################


engine = sa.create_engine(db_conn)
Session = orm.scoped_session(
        orm.sessionmaker(autocommit=False,
                         autoflush=False,
                         bind=engine))
Base = declarative_base(bind=engine)

session = Session()


class Post(Base):
    __tablename__ = table_prefix + "posts"
    __table_args__ = {'autoload': True}
    id = sa.Column("ID", sa.Integer, primary_key=True)
    author_id = sa.Column("post_author",
            sa.ForeignKey(table_prefix + 'users.ID'))
    author = orm.relation("User", primaryjoin="Post.author_id == User.id")
    term_relationship = orm.relation("TermRelationship",
                                 primaryjoin="Post.id == TermRelationship.id")

    def categories(self):
        return [r.taxonomy.term.name for r in self.term_relationship
                if r.taxonomy.taxonomy == "category"]

    def tags(self):
        return [r.taxonomy.term.name for r in self.term_relationship
                if r.taxonomy.taxonomy == "post_tag"]

    def __repr__(self):
        return u"<Post '{0}' id={1} status='{2}'>".format(
                self.post_title, self.id, self.post_status)

    def permalink(self):
        site_url = get_blog_url()
        structure = get_blog_permalink_structure()
        structure = structure.replace("%year%", str(self.post_date.year))
        structure = structure.replace("%monthnum%",
                str(self.post_date.month).zfill(2))
        structure = structure.replace("%day%", str(self.post_date.day).zfill(2))
        structure = structure.replace("%hour%",
                str(self.post_date.hour).zfill(2))
        structure = structure.replace("%minute%",
                str(self.post_date.minute).zfill(2))
        structure = structure.replace("%second%",
                str(self.post_date.second).zfill(2))
        structure = structure.replace("%postname%", self.post_name)
        structure = structure.replace("%post_id%", str(self.id))
        try:
            structure = structure.replace("%category%", self.categories()[0])
        except IndexError:
            pass
        try:
            structure = structure.replace("%tag%", self.tags()[0])
        except IndexError:
            pass
        structure = structure.replace("%author%", self.author.user_nicename)
        return site_url.rstrip("/") + "/" + structure.lstrip("/")


class User(Base):
    __tablename__ = table_prefix + "users"
    __table_args__ = {'autoload': True}
    id = sa.Column("ID", sa.Integer, primary_key=True)

    def __repr__(self):
        return u"<User '{0}'>".format(self.user_nicename)


class Term(Base):
    __tablename__ = table_prefix + "terms"
    __table_args__ = {'autoload': True}
    id = sa.Column("term_id", sa.Integer, primary_key=True)
    
    def __repr__(self):
        return u"<Term '{0}'>".format(self.name)


class TermTaxonomy(Base):
    __tablename__ = table_prefix + "term_taxonomy"
    __table_args__ = {'autoload': True}
    id = sa.Column('term_taxonomy_id', sa.Integer, primary_key=True)
    term_id = sa.Column("term_id",
            sa.ForeignKey(table_prefix + "terms.term_id"))
    term = orm.relation("Term", primaryjoin="Term.id == TermTaxonomy.term_id")
    

class TermRelationship(Base):
    __tablename__ = table_prefix + "term_relationships"
    __table_args__ = {'autoload': True}
    id = sa.Column('object_id', sa.ForeignKey(table_prefix + "posts.ID"),
                   primary_key=True)
    taxonomy_id = sa.Column("term_taxonomy_id", sa.ForeignKey(
            table_prefix + "term_taxonomy.term_id"), primary_key=True)
    taxonomy = orm.relation("TermTaxonomy",
            primaryjoin="TermTaxonomy.id == TermRelationship.taxonomy_id")


class WordpressOptions(Base):
    __tablename__ = table_prefix + "options"
    __table_args__ = {'autoload': True}
                            

def get_published_posts(blog_id=0):
    return [p for p in session.query(Post).all() if p.post_status=="publish"
            and p.post_type=="post"]


def get_blog_url(blog_id=0):
    return session.query(WordpressOptions).filter(
            WordpressOptions.blog_id==blog_id).\
            filter(WordpressOptions.option_name=="siteurl").\
            first().option_value


def get_blog_permalink_structure(blog_id=0):
    return session.query(WordpressOptions).filter(
            WordpressOptions.blog_id==blog_id).\
            filter(WordpressOptions.option_name=="permalink_structure").\
            first().option_value
    
if __name__ == '__main__':
    #Output textile files in ./_posts
    if os.path.isdir("_posts"):
        print "There's already a _posts directory here, "\
                "I'm not going to overwrite it."
        sys.exit(1)
    else:
        os.mkdir("_posts")

    post_num = 1
    for post in get_published_posts():
        yaml_data = {
            "title": post.post_title,
            "date": post.post_date.strftime("%Y/%m/%d %H:%M:%S"),
            "permalink": post.permalink(),
            "categories": ", ".join(post.categories()),
            "tags": ", ".join(post.tags()),
            "guid": post.guid
            }
        fn = u"{0}. {1}.html".format(
                str(post_num).zfill(4),
                re.sub(r'[/!:?\-,\']', '', post.post_title.strip().lower().replace(' ', '_')))
        print "writing " + fn
        f = codecs.open(os.path.join("_posts", fn), "w", "utf-8")
        f.write("---\n")
        f.write(yaml.safe_dump(yaml_data, default_flow_style=False, allow_unicode=True).decode("utf-8"))
        f.write("---\n")
        f.write(post.post_content.replace(u"\r\n", u"\n"))
        f.close()
        post_num += 1
