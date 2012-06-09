The Makeup of a Blogofile Site
******************************
Blogofile is a website `compiler`_, but instead of translating something like C++ source code into an executable program, Blogofile takes `Mako`_ templates, and other Blogofile features, and compiles HTML for viewing in a web browser. This chapter introduces the basic building blocks of a Blogofile directory containing such source code.

An Example
==========
The best way to understand how Blogofile works is to look at an example. Create a new directory and inside it run::

 blogofile init simple_blog

This command creates a very simple blog that you can use to learn how Blogofile works as well as to provide a clean base from which you can create your own Blogofile based website.

For a more complete example, you can checkout the code for the same website you're reading right now, blogofile.com::

  blogofile init blogofile.com

This command downloads the very latest blogofile.com website source code, which requires that you have `git`_ installed on your system. If you don't have it, you can just download the `zip file`_ instead.

The rest of this document will assume that you're using the simple_blog template. It is the defacto reference platform for Blogofile.

Directory Structure
===================

Inside the source directory are the following files (abbreviated)::

  |-- _config.py
  |-- _controllers
  |   |-- blog
  |   |   |-- archives.py
  |   |   |-- categories.py
  |   |   |-- chronological.py
  |   |   |-- feed.py
  |   |   |-- __init__.py
  |   |   |-- permapage.py
  |   |   `-- post.py
  |-- _filters
  |   |-- markdown_template.py
  |   |-- syntax_highlight.py
  |-- index.html.mako
  |-- _posts
  |   |-- 001 - post 1.markdown
  |   |-- 002 - post 2.markdown
  `-- _templates
      |-- atom.mako
      |-- base.mako
      |-- chronological.mako
      |-- footer.mako
      |-- header.mako
      |-- head.mako
      |-- permapage.mako
      |-- post_excerpt.mako
      |-- post.mako
      |-- rss.mako
      `-- site.mako
    
The basic building blocks of a Blogofile site are:

 * **_config.py** - Your main Blogofile configuration file. See :ref:`config-file`
 * **Templates** - Templates dynamically create pages on your site. ``index.html.mako`` along with the entire ``_templates`` directory are examples. See :ref:`templates`
 * **Posts** - Your blog posts, contained in the ``_posts`` directory. See :ref:`posts`
 * **Filters** - contained in the ``_filters`` directory, filters can process textual data like syntax highlighters, translators, swear word censors etc. See :ref:`filters`
 * **Controllers** - contained in the ``_controllers`` directory, controllers create dynamic sections of your site, like blogs. See :ref:`controllers`

Any file or directory not starting with an underscore, and not ending in ".mako", are considered regular files (eg. ``css/site.css`` and ``js/site.js``). These files are copied directly to your compiled site.

Building the Site
=================

Now that you have an example site initialized, we can compile the source to create a functioning website. 

Run the following to compile the source in the current directory::

    blogofile build

Blogofile should run without printing anything to the screen. If this is the case, you know that it ran successfully. Inside the _site directory you have now built a complete website based on the source code in the current directory. You can now upload the contents of the _site directory to your webserver or you can test it out in the embedded webserver included with Blogofile::

    blogofile serve 8080

Go to `http://localhost:8080 <http://localhost:8080>`_ to see the site served from the embedded webserver. You can quit the server by pressing ``Control-C``.

Understanding the Build Process
===============================

When the Blogofile build process is invoked, it follows this conceptual order of events:

* A ``_config.py`` file is loaded with your custom settings. See :ref:`config-file`.

* If the blog feature is enabled (:ref:`config-blog-enabled`), the blog posts in the ``_posts`` directory are processed and made available to templates. See :ref:`Posts`.

* Filters in the ``_filters`` directory are made available to templates. See :ref:`filters`.

* Files and sub-directories are recursively processed and copied over to the ``_site`` directory which becomes the compiled HTML version of the site:

  * If the filename ends in ``.mako``, it is considered a page template. It is rendered via Mako, then copied to the ``_site`` directory stripped of the ``.mako`` extension. See :ref:`templates`.

  * If the filename or directory starts with an underscore, it is ignored and not copied to the ``_site`` directory (other ignore patterns may be setup using :ref:`config-file-ignore-patterns` in ``_config.py``.)

* Controllers from the ``_controllers`` directory are run to build dynamic sections of your site, for example, all of the blog features: permalinks, archives, categories etc. See :ref:`controllers`.

Build Process Flowchart
-----------------------

Click for larger SVG view

.. raw:: html
   
   <a href="/documentation/graphs/build_process.dot.svg"><img src="/documentation/graphs/build_process.dot.png"></a>

.. _Mako: http://www.makotemplates.org

.. _zip file: http://github.com/EnigmaCurry/blogofile.com/zipball/master

.. _compiler: http://en.wikipedia.org/wiki/Compiler

.. _git: http://www.git-scm.org

.. _Python: http://www.python.org

.. _timezone: http://en.wikipedia.org/wiki/List_of_zoneinfo_time_zones

