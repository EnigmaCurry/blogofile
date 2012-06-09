.. _config-file:

Configuration File
==================

Blogofile looks for a file called ``_config.py`` in the root of your source directory; this is your site's main configuration file. Blogofile tries to use sensible default values for anything you don't configure explicitly in this file. Although every site must have a ``_config.py``, it can start out completely blank.

``_config.py`` is just regular `Python`_ source code. If you don't know any Python, don't worry, there's actually very little you need to change in this file to get started.

.. _config-context:

Context of _config.py
|||||||||||||||||||||

``_config.py`` is run within a context that is prepared by Blogofile before executing. This context includes the following objects:

* **controllers** - Settings for each controller (See :ref:`controllers`).
* **filters** - Settings for each filter (See :ref:`filters`).
* **site** - General Settings pertaining to your site, eg: site.url.

All of these are instances of the `HierarchicalCache`_ class. `HierarchicalCache`_ objects behave a bit differently than typical Python objects: accessed attributes that do not exist, do not raise an `AttributeError`_. Instead, they instantiate the non-existing attribute as a nested `HierarchicalCache`_ object.

This style of configuration provides a seperate namespace for each feature of your blogofile site, and also allows for Blogofile to contain configuration settings for controllers or filters that may or may not be currently installed. For example, your ``_config.py`` might have the following setting for a photo gallery controller::

  controllers.photo_gallery.albums.photos_per_page = 5

In the above example, ``controllers``, ``photo_gallery``, and ``albums``, are all instances of `HierarchicalCache`_. ``photos_per_page`` is an integer that is an attribute on the ``albums`` `HierarchicalCache`_.

Because this setting is contained in a `HierarchicalCache`_ object, if the photo gallery controller is not installed, the setting will simply be ignored.


.. _site-configuration:

Site Configuration
||||||||||||||||||

In Blogofile, the "site" corresponds with the ``_site`` directory that blogofile builds. Even if your site is primarily used as a blog, think of the "site" as the parent of the blog. The site has it's own namespace within ``_config.py`` called ``site``.

.. _config-site-url:

site.url
++++++++
String

This is the root URL for your website. This is the URL that your blogofile site will be hosted at::

    site.url = "http://www.xkcd.com"

.. _config-file-ignore-patterns:

site.file_ignore_patterns
+++++++++++++++++++++++++
List

This is a list of regular expressions that describe paths to ignore when processing your source directory. The most important one (and one you should not remove) is ``".*/_.*"`` which ignores all files and directories that start with an underscore (like ``_config.py`` and ``_posts``)::

    site.file_ignore_patterns = [
    # All files that start with an underscore
    ".*/_.*",
    # Emacs temporary files
    ".*/#.*",
    # Emacs/Vim temporary files
    ".*~$",
    # Vim swap files
    ".*/\..*\.swp$",
    # VCS directories
    ".*/\.(git|hg|svn|bzr)$",
    # Git and Mercurial ignored files definitions
    ".*/.(git|hg)ignore$",
    # CVS dir
    ".*/CVS$",
    ]

Blog Configuration
||||||||||||||||||

The core of Blogofile actually does not know what a blog is. Blogofile itself just provides a runtime environment for templates, controllers and filters. A Blogofile blog is actually built by creating a blog controller (see :ref:`Controllers`.) A default implementation of a blog controller is provided with the Blogofile ``simple_blog`` template and should be sufficient for most users.

All controllers in Blogofile have their own seperate namespace in ``_config.py`` under ``controllers``. For convenience, you would usually reference the blog controller like so in ``_config.py``::

    blog = controllers.blog

.. _config-blog-enabled:

blog.enabled
++++++++++++
Boolean
  
This turns on/off the blog feature. Blogofile is obviously geared toward sites that have blogs, but you don't *need* to have one. If this is set to True, Blogofile requires several blog specific templates to exist in the ``_templates`` directory as described in :ref:`required-templates`::

    blog.enabled = True

.. _config-blog-path:

blog.path
+++++++++
String

This is the path of the blog off of the :ref:`config-site-url`. For example, if :ref:`config-site-url` is ``http://www.xkcd.com/stuff`` and blog.path is ``/blag`` your full URL to your blog will be ``http://www.xkcd.com/sfuff/blag``::

    blog.path = "/blog"

blog.name
+++++++++
String
  
This is the name of your blog::

    blog.name = "xkcd - The blag of the webcomic"

blog.description
++++++++++++++++
String

This is a (short) description of your blog. Many RSS readers support/expect a description for feeds::

    blog.description = "A Webcomic of Romance, Sarcasm, Math, and Language"

blog.timezone
+++++++++++++
String

This is the `timezone`_ that you normally post to your blog from::

    blog.timezone = "US/Eastern"

You can see all of the appropriate values by running::

    python -c "import pytz, pprint; pprint.pprint(pytz.all_timezones)" | less

blog.posts_per_page
+++++++++++++++++++
Integer

This is the number of blog posts you want to display per page::

    blog.posts_per_page = 5

.. _comprehensive-config-values:


blog.auto_permalink.enabled
+++++++++++++++++++++++++++
Boolean

This turns on automatic permalink generation. If your post does not include a permalink field, then this allows for the automatic generation of the permalink::

    blog.auto_permalink.enabled = True

.. _config-blog-auto-permalink:

blog.auto_permalink.path
++++++++++++++++++++++++
String

This is the format that automatic permalinks should take on, starting with the path after the blog domain name. eg: ``/blag/:year/:month/:day/:title`` creates a permalink like ``http://www.xkcd.com/blag/2009/08/18/post-one``::

    blog.auto_permalink.path = ":blog_path/:year/:month/:day/:title"

Available replaceable items in the string:

 * :blog_path - The root of the blog
 * :year - The post year
 * :month - The post month
 * :day - The post day
 * :title - The post title
 * :uuid - sha hash based on title
 * :filename - the filename of the post (minus extension)

.. _config-disqus-enabled:

blog.disqus.enabled
+++++++++++++++++++
Boolean

Turns on/off `Disqus`_ comment system integration::

    blog.disqus.enabled = False

.. _config-disqus-name:

blog.disqus.name
++++++++++++++++
String 

The Disqus website 'short name'::

    blog.disqus.name = "your_disqus_name"

.. _config-syntax-highlight-enabled:

blog.custom_index
+++++++++++++++++
Boolean

When you configure :ref:`config-blog-path`, Blogofile by default writes a chronological listing of the latest blog entries at that location. With this option you can turn that behaviour off and your index.html.mako file in that same location will be your own custom template::

    blog.custom_index = False

.. _config-post-excerpt-enabled:

blog.post_excerpts.enabled
++++++++++++++++++++++++++
Boolean

Post objects have a ``.content`` attribute that contains the full content of the blog post. Some blog authors choose to only show an excerpt of the post except for on the permalink page. If you turn this feature on, post objects will also have a ``.excerpt`` attribute that contains the first :ref:`config-post-excerpt-word-length` words::

    blog.post_excerpts.enabled = True

If you don't use post excerpts, you can turn this off to decrease render times.

.. _config-post-excerpt-word-length:

blog.post_excerpts.word_length
++++++++++++++++++++++++++++++
Integer

The number of words to have in post excerpts::

    blog.post_excerpts.word_length = 25

.. _config-blog-pagination-dir:

blog.pagination_dir
+++++++++++++++++++
String 

The name of the directory that contains more pages of posts than can be shown on the first page.

Defaults to ``page``, as in ``http://www.test.com/blog/page/4``::

    blog.pagination_dir = "page"

.. _config-blog-post-default-filters:

blog.post_default_filters
+++++++++++++++++++++++++
Dictionary

This is a dictionary of file extensions to default filter chains (see :ref:`filters`) to be applied to blog posts. A default filter chain is applied to a blog post only if no filter attribute is specified in the blog post YAML header::

    blog.post_default_filters = {
        "markdown": "syntax_highlight, markdown",
        "textile": "syntax_highlight, textile",
        "org": "syntax_highlight, org",
        "rst": "syntax_highlight, rst",
        "html": "syntax_highlight"
    }

Build Hooks
|||||||||||

.. _config-pre-build:

pre_build
+++++++++
Function

This is a function that gets run before the _site directory is built

.. _config-post-build:

post_build
++++++++++
Function

This is a function that gets run after the _site directory is built
.. _config-post-build:


build_finally
+++++++++++++
Function

This is a function that gets run after the _site directory is built OR whenever a fatal error occurs. You could use this function to perform a cleanup function after building, or to notify you when a build fails. 

.. _timezone: http://en.wikipedia.org/wiki/List_of_zoneinfo_time_zones

.. _Disqus: http://www.disqus.com

.. _Pygments Styles: http://pygments.org/docs/styles

.. _Emacs: http://www.gnu.org/software/emacs

.. _Python: http://www.python.org

.. _HierarchicalCache: http://github.com/EnigmaCurry/blogofile/blob/master/blogofile/cache.py#L22

.. _AttributeError: http://docs.python.org/library/exceptions.html#exceptions.AttributeError
