Introduction
************

* Definition: **Blogophile** (n):
   A person who is fond of or obsessed with blogs or blogging.

* Definition: **Blogofile** (n):
   A static website compiler and blog engine, written and extended in `Python`_.


Welcome to Blogofile
====================

Blogofile is a static website compiler, primarily (though not exclusively) designed to be a simple blogging engine. It requires no database and no special hosting environment. You customize a set of templates with `Mako <http://www.maktotemplates.org>`_, create posts in a markup language of your choice (see :ref:`post-content`) and Blogofile renders your entire website as static HTML and Atom/RSS feeds which you can then upload to any old web server you like. 

Why you should consider Blogofile
=================================

* Blogofile is **free open-source** software, released under a non-enforced `MIT License`_.
* Blogofile sites are **fast**, the web server doesn't need to do any database lookups nor any template rendering.
* Blogofile sites are **inexpensive** to host. Any web server can host a blogofile blog.
* Blogofile is **modern**, supporting all the common blogging features:

 * Categories and Tags.
 * Comments, Trackbacks, and Social Networking mentions (Twitter,
   Reddit, FriendFeed etc), all with effective spam filtering using
   `Disqus <http://www.disqus.com>`_.
 * RSS and Atom feeds, one for all your posts, as well as one per
   category. Easily create additional feeds for custom content.
 * Syntax highlighting for source code listings.
 * Ability to create or share your own plugins in your own
   userspace (see :ref:`Filters <filters>` and :ref:`Controllers <controllers>`)

* Blogofile is **secure**, there's nothing executable on the server `to exploit <http://wordpress.org/news/2010/12/3-0-4-update/>`_.
* Blogofile works **offline**, with a built-in web server you can work on your site from anywhere.
* Blogofile is **file based**, so you can edit it with your favorite text editor, not some crappy web interface.
* Seamless :ref:`Git Integration <vcs-integration>`. Publish to your blog with a simple ``git push``. This also makes **backups** dirt simple.

.. _install-blogofile:

Installing Blogofile
====================
Blogofile is under active development, but strives to be usable and bug-free before the 1.0 release.

Prerequisites
-------------

Make sure you have `Python`_ and `Setuptools`_ installed. On Ubuntu you just need to run::

 sudo apt-get install python-setuptools

Install
-------
Download and install Blogofile with::

 easy_install Blogofile

You can also get the latest development source code from github::

 git clone git://github.com/EnigmaCurry/blogofile.git

.. _MIT License: http://www.blogofile.com/LICENSE.html

.. _Python: http://www.python.org

.. _Setuptools: http://pypi.python.org/pypi/setuptools
