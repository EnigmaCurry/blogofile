Migrating Existing Blogs to Blogofile
=====================================

Unless you're starting a brand new blog from scratch, you're probably going to want to migrate an existing blog to Blogofile. When migrating, you have to consider several things:

 * Migrating existing blog posts.
 * Migrating existing blog comments.
 * Migrating permalinks and other search engine indexed URLs.

Wordpress
---------

Comments
++++++++

Before you bring your Wordpress blog offline, install the `Disqus wordpress plugin`_. With this plugin, you can export all your comments from your wordpress database offsite into your Disqus account.

In your blogofile config file, set the :ref:`config-disqus-enabled` and :ref:`config-disqus-name` settings appropriately.

Posts
+++++

Download the converter script:

* `wordpress2blogofile.py`_

Install SQL Alchemy::

 easy_install sqlalchemy

If your database is MySQL based, you'll also need to download `MySQLdb`_, which you can apt-get on Ubuntu::

 sudo apt-get install python-mysqldb

If you're using some other database, install the appropriate `DBAPI`_.

Edit ``wordpress_schema.py``:

* ``table_prefix`` should be the same as you setup in wordpress, (or blank "" if none)
* ``db_conn`` point to your database server. The example is for a MySQL hosted database, but see the `SQL Alchemy docs`_ if you're using something else.

In a clean directory run the export script::

 python wordpress2blogofile.py

If everything worked, you should now have a ``_posts`` directory containing valid Blogofile format posts which you can copy to your blogofile directory.

Permalinks
++++++++++

You're probably going to want to retain the exact same permalinks that your wordpress blog had. If you've been blogging for long, Google has inevitably indexed your blog posts and people may have linked to you; you don't want to change the permalink URLs for your posts.

The converter script should transfer over the permalinks directly into the :ref:`post-yaml` of the blog post. You may also want to configure the :ref:`config-blog-auto-permalink` setting in your configuration file to create the same style of permalink that you're using in wordpress.

Moveable Type
-------------

to be written.

.. _Disqus wordpress plugin: http://wordpress.org/extend/plugins/disqus-comment-system
.. _wordpress2blogofile.py: http://github.com/EnigmaCurry/blogofile/raw/master/converters/wordpress2blogofile.py
.. _MySQLdb: http://sourceforge.net/projects/mysql-python/
.. _DBAPI: http://www.sqlalchemy.org/docs/05/dbengine.html#supported-dbapis
.. _SQL Alchemy docs: http://www.sqlalchemy.org/docs/05/dbengine.html#create-engine-url-arguments
