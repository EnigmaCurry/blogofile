.. _filters:

Filters
******************************
Filters are Blogofile's text processor plugin system. They create callable functions in templates and blog posts that can perform manipulation on a block of text. Ideas for filters:

* Markup languages.
* A code syntax highlighter.
* A flash video plugin helper.
* A swear word filter.
* A foreign language translator.

.. _filter-simple-example:

A Simple Filter
---------------

Here's a swear word filter that replaces nasty words with the word ``kitten``. The file is called ``_filters/playnice.py``::

 #Replace objectionable language with kittens.
 #This is just an example, it's far from exhaustive.
 import re

 seven_words = re.compile(
   r"\Wfrak\W|\Wsmeg\W|\Wjoojooflop\W|\Wswut\W|\Wshazbot\W|\Wdoh\W|\Wgorram\W|\Wbelgium\W",
   re.IGNORECASE)

 def run(content):
     return seven_words.sub(" kitten ", content)

This filter (once it's in your ``_filters`` directory) is available to all templates and blog posts.

Filter Chains
-------------

Filters can be chained together, one after the other, so that you can perform multiple text transformations on a peice of text.

Suppose you have the following filters in your ``_filters`` directory:
 
* **markdown.py** - Transforms `Markdown`_ formatted text into HTML.
* **playnice.py** - The swear word filter above.
* **syntax_highlight.py** - A code syntax highligher

A filter chain of ``markdown, playnice, syntax_highlight`` will apply those three filters (seperated by commas) in the order given.

Using Filters in a Template
---------------------------

The filter module provides the method called ``run_chain``. You can use this directly in your mako templates::

 The following text is filtered:

 ${bf.filter.run_chain('playnice, syntax_highlight', 'some shazbot text')}

However, it's kind of a pain to always wrap the text you want to filter in that function call. Writing a mako ``<%def>`` block can create some nice syntactic sugar for us. Define the following in your base template so that all templates that inherit from it can benefit from it::

 <%def name="filter(chain)">
  ${bf.filter.run_chain(chain, capture(caller.body))}
 </%def>

How to use it in a template::

 <%self:filter chain="playnice, syntax_highlight">Belgium: Less offensive 
   words have been created in the many languages of the galaxy, such as
   joojooflop, swut and Holy Zarquon's Singing Fish. </%self:filter>

All the text between the ``<%self:filter>`` start and end tags is filtered by the specified filter chain.

Using Filters in a Blog Post
----------------------------

Filter chains can be applied to blog posts in the post YAML::

 ---
 date: 2009/12/01 11:17:00
 permalink: http://www.blogofile.com/whatever
 title: A markdown formatted test post
 filter: markdown, playnice
 ---
 This is a **markdown** formatted post with all the frak words filtered.

Filters on blog posts are applied to the entire blog post; you cannot apply a filter to only a portion of the text like you can with templates. However, there is nothing preventing you from writing a filter that looks for special syntax in your posts and filters selectively (the syntax_highlight filter from simple_blog does exactly this). This allows for more end user customizability. 

If no filter is specified for your post, Blogofile looks at a config option called :ref:`config-blog-post-default-filters` which maps the file extension of the post file to a filter chain. Defaults include ``markdown`` and ``textile``.

You can turn off all filters for the post, including the default ones, by specifing a filter chain of ``none``.

Filter structure
--------------------

Filters can be single .py files inside the _filters directory, as in the ``playnice.py`` example above, or they can be full python modules (Python modules are directories with a ``__init__.py`` file). This second method will let you split your filters among multiple files.

Filters have a standardized configuration protocol. All filters define a dictionary called ``config``. By default it contains the following values::

    config = {"name"        : None,
              "description" : None,
              "author"      : None,
              "url"         : None}

These settings are as follows:

 * name - The human friendly name for the controller.
 * author - The name or group responsible for writing the controller.
 * description - A brief description of what the controller does.
 * url - The URL where the controller can be downloaded on the authors site.

These are just the default settings, a filter author may provide as many configuration settings as he wants. 

A user can override any configuration setting in their ``_config.py``::

    filters.playnice.zealous_and_vigorous_parsing = True


.. _Markdown: http://en.wikipedia.org/wiki/Markdown
