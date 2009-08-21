#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Wordpress schema (2.7)"""

__author__ = "Ryan McGuire (ryan@enigmacurry.com)"
__date__   = "Sun Feb 15 14:41:26 2009"

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declarative_base

#########################
## Config
#########################
table_prefix = ""
db_conn = "mysql://username:password@localhost/database_name"
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
    __tablename__ = table_prefix + "wp_posts"
    __table_args__ = {'autoload': True}
    id = sa.Column("ID", sa.Integer, primary_key=True)
    author_id = sa.Column("post_author", sa.ForeignKey(table_prefix+'wp_users.ID'))
    author = orm.relation("User", primaryjoin="Post.author_id == User.id")
    term_relationship = orm.relation("TermRelationship",
                                     primaryjoin="Post.id == TermRelationship.id")
    def categories(self):
        return [r.taxonomy.term.name for r in self.term_relationship if r.taxonomy.taxonomy == "category"]
    def tags(self):
        return [r.taxonomy.term.name for r in self.term_relationship if r.taxonomy.taxonomy == "post_tag"]

    def __repr__(self):
        return "<Post '%s' id=%s status='%s'>" % (self.post_title,self.id,self.post_status)

    def permalink(self):
        site_url = get_blog_url()
        structure = get_blog_permalink_structure()
        structure = structure.replace("%year%", str(self.post_date.year))
        structure = structure.replace("%monthnum%", str(self.post_date.month).zfill(2))
        structure = structure.replace("%day%", str(self.post_date.day).zfill(2))
        structure = structure.replace("%hour%", str(self.post_date.hour).zfill(2))
        structure = structure.replace("%minute%", str(self.post_date.minute).zfill(2))
        structure = structure.replace("%second%", str(self.post_date.second).zfill(2))
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
    __tablename__ = table_prefix + "wp_users"
    __table_args__ = {'autoload': True}
    id = sa.Column("ID", sa.Integer, primary_key=True)
    def __repr__(self):
        return "<User '%s'>" % self.user_nicename

class Term(Base):
    __tablename__ = table_prefix + "wp_terms"
    __table_args__ = {'autoload': True}
    id = sa.Column("term_id", sa.Integer, primary_key=True)
    
    def __repr__(self):
        return "<Term '%s'>" % self.name

class TermTaxonomy(Base):
    __tablename__ = table_prefix + "wp_term_taxonomy"
    __table_args__ = {'autoload': True}
    id = sa.Column('term_taxonomy_id', primary_key=True)
    term_id = sa.Column("term_id", sa.ForeignKey(table_prefix+"wp_terms.term_id"))
    term = orm.relation("Term", primaryjoin="Term.id == TermTaxonomy.term_id")
    
class TermRelationship(Base):
    __tablename__ = table_prefix + "wp_term_relationships"
    __table_args__ = {'autoload': True}
    id = sa.Column('object_id', sa.ForeignKey(table_prefix+"wp_posts.ID"),
                   primary_key=True)
    taxonomy_id = sa.Column("term_taxonomy_id", sa.ForeignKey(
            table_prefix+"wp_term_taxonomy.term_id"), primary_key=True)
    taxonomy = orm.relation("TermTaxonomy", primaryjoin=
                            "TermTaxonomy.id == TermRelationship.taxonomy_id")

class WordpressOptions(Base):
    __tablename__ = table_prefix + "wp_options"
    __table_args__ = {'autoload': True}
                            
def get_published_posts(blog_id=0):
    return [p for p in session.query(Post).all() if p.post_status=="publish" and p.post_type=="post"]

def get_blog_url(blog_id=0):
    return session.query(WordpressOptions).filter(WordpressOptions.blog_id==blog_id).\
        filter(WordpressOptions.option_name=="siteurl").first().option_value

def get_blog_permalink_structure(blog_id=0):
    return session.query(WordpressOptions).filter(WordpressOptions.blog_id==blog_id).\
        filter(WordpressOptions.option_name=="permalink_structure").first().option_value
    
