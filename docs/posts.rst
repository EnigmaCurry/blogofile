.. _posts:

Posts
*****

Posts are interpreted by the blog controller that you get when you instantiate the simple_blog; they have no particular meaning to the core runtime of Blogofile. If you wanted, you could reimplement the blog controller yourself and use whatever post formatting you wished. It's expected that most users will just use the default blog controller, so this Post documentation is here for convenience.

Blog posts go inside the **_posts** directory. Without the blog controller enabled, the **_posts** directory is ignored because it starts with an underscore.

Each post is a seperate file and you can name the files whatever you want, but it's suggested to prefix your posts with a number like ``0001``, ``0002`` etc. so that when you look at the files in a directory they will be naturally ordered sequentially. It's important to realize that this order is not the same order that the blog controller uses in chronlogical listings. Instead it sorts the posts based on the date field described below.

An Example Post
---------------
Here's an example post::

 ---
 categories: Category One, Category Two
 date: 2009/08/18 13:09:00
 permalink: http://www.blogofile.com/2009/08/18/first-post
 title: First Post
 ---
 This is the first post 

The post is divided into two parts, the YAML header and the post content.

You can see more `examples of Blogofile posts <http://www.blogofile.com/demo/sample_posts.html>`_ on the project site. 

.. _post-yaml:

YAML Header
-----------
The `YAML`_ portion is between the two ``---`` lines, and it describes all of the metadata for the post. You can define as many fields as you like, but there are some names that are reserved for general purpose use:

* **title**
    A one-line free-form title for the post.
* **date**
    The date that the post was originally created. (year/month/day hour:minute:second).
* **updated**
    The date that the post was last updated. (year/month/day hour:minute:second).
* **categories**
    A list of categories that the post pertains to, each seperated by commas. You don't have to configure the categories beforehand, you are defining them right here.
* **tags**
    A list of tags that the post pertains to, each seperated by commas.
* **permalink**
    The full permanent URL for this post. This is optional, one will be generated automatically if left blank. (see :ref:`config-blog-auto-permalink`)
* **filters**
    The filter chain to run on the post content. (see :ref:`filters`)
* **filter**
    A synonym for filters. (see :ref:`filters`)
* **guid**
    A unique hash for the post, if not provided it is assumed that the permalink is the guid.
* **author**
    The name of the author of the post.
* **draft**
    If 'true' or 'True', the post is considered to be only a draft and not to be published. A permalink will be generated for the post, but the post will not show up in indexes or RSS feeds. You would have to know the full permalink to ever see the page.
* **source**
    Reserved internally.
* **yaml**
    Reserved internally.
* **content**
    Reserved internally.
* **filename**
    Reserved internally.

This list is also defined in the blogofile source code under ``blogofile.post.reserved_field_names`` and can be accessed as a dictionary at runtime.

.. _post-content:

Post Content
------------
The post content is written using a markup language, currently Blogofile supports several to choose from:

* `Markdown`_ (files end in .markdown)
* `Textile`_ (files end in .textile)
* `reStructuredText`_ (files end in .rst)
* or plain old HTML (files end in .html by convention, but if it's not one of the above, posts default to HTML anyway)

Adding your own markup formats is easy, you just implement it as a filter (see :ref:`Filters`)

The content of the post goes directly after the YAML portion and uses whatever markup language is indicated by the file extension of the post file.

Referencing posts in templates
------------------------------

All the posts are stored in a cache object called ``bf``. This object is exposed to all templates and you can reference it directly with ``${bf.config.blog.posts}``. They are ordered sequentially by date. See :ref:`adding-blogofile-features-to-our-templates` for an example.

.. _YAML: http://en.wikipedia.org/wiki/YAML

.. _Markdown: http://en.wikipedia.org/wiki/Markdown

.. _Textile: http://en.wikipedia.org/wiki/Textile_(markup_language)

.. _Org Mode: http://orgmode.org/

.. _reStructuredText: http://docutils.sourceforge.net/rst.html
