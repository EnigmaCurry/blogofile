.. _templates:

Templates
*********

Templates are at the very heart of Blogofile; they control every aspect of how the site is structured. Blogofile uses the `Mako`_ templating engine which has an active community and `great documentation`_. Blogofile doesn't try to limit what you can do with your templates, you've got the full power of Mako so go ahead and use it.

Blogofile makes a distinction between two basic kinds of templates:

* **Page** templates
* **Reusable** templates

Page templates represent a single unique page (or URL) on your site. These are files somwhere in your source directory that end in ``.mako`` and never reside in a directory starting with an underscore. Page templates are rendered to HTML and copied to the ``_site`` directory in the same location where they reside in the source directory. Examples: an index page, a contact page, or an "about us" page.

Reusable templates are contained in the _templates directory. These are features that you want to include on many pages. Examples: headers, footers, sidebars, blog post layouts etc. Reusable templates do not represent any particular page (or URL) but are rather `inherrited`_ or `included`_ inside other templates or :ref:`controllers` and usually reused on many diverse pages.

A Simple Example Using Just Mako
--------------------------------

It would be redundant to describe all the things you can do with Mako when `great documentation`_ already exists, but a few simple examples of templates are in order.

The first thing a website needs is an index or 'home' page. Here's how you create one in blogofile:

In the root of your source directory create a file called ``index.html.mako``::

  <%inherit file="_templates/site.mako" />
  This is the index page contents.

Well, there's not much in there, but that's by design. To effectively use Mako, you're going to want to use `inheritance <http://www.makotemplates.org/docs/inheritance.html>`_ to allow you to abstract out the things that you want to repeat on every page (headers, footers, sidebars etc) from the things that don't repeat: the content of the page.

The ``index.html.mako`` inherits from a **reusable template** called ``site.mako``. Create a file called ``_templates/site.mako``::

   <html>
     <body>
      ${self.header()}
       <div id="main_block">
         ${next.body()}
       </div>
       ${self.footer()}
     </body>
   </html>
   <%def name="header()">
     This is a header you want on every page
     <hr/>
   </%def>
   <%def name="footer()">
     <hr/>
     This is a footer you want on every page
   </%def>

At the bottom of ``site.mako`` there are two ``<%def>`` blocks: header and footer. Think of these ``<%def>`` blocks as functions that can be reused multiple times. Each of these defs are referenced inside the ``<html>`` tag above (eg. ``${self.header()}``). Referencing the def block simply deposits the contents of the ``<def>`` wherever it's referenced. 

You could simply write the header and footer inline in the HTML and you'd still get the same effect of having them appear on every page that inherits from ``site.mako``, however if you create them as ``<%def>`` blocks, you can redefine these blocks on child templates so that a different header or footer can appear on some pages while retaining the rest of the look and feel of the ``site.mako`` template. 

One special reference is also made to ``${next.body()}``. This deposits the contents of any child templates that inherit from this template. In our example, ``index.html.mako`` inherits from ``site.mako``, so the text ``this is the index page contents`` is deposited inside the ``<div id="main_block">`` in the resulting HTML file which looks something like this::

  <html>
    <body>
      This is a header you want on every page
      <hr/>
       <div id="main_block">
        This is the index page contents.
       </div>
      <hr/>
      This is a footer you want on every page
    </body>
  </html>

.. _adding-blogofile-features-to-our-templates:

Adding Blogofile Features To Our Templates
------------------------------------------

In the last section we introduced a simple template called ``index.html.mako``. This template is the home page of our site, and so far only includes regular mako functionality. Now let's introduce some Blogofile action! 

Let's say we want to include on our home page a list of the 5 most recent posts from our blog. As long as :ref:`config-blog-enabled` is turned on, each template can get access to our blog posts through a cache object called ``bf``. We can modify our ``index.html.mako`` to get the list of recent posts::

  <%inherit file="_templates/site.mako" />
  Here's the five most recent posts from the blog:

  <ul>
  % for post in bf.config.blog.posts[:5]:
    <li><a href="${post.path}">${post.title}</a></li>
  % endfor
  </ul>

If you're familiar with for-loops in Python, this should look somewhat similar. We create an unordered list tag and inside that list we iterate over a special Blogofile object containing all of our posts. We limit ourselves to the first 5 posts by slicing the list of posts from 0 to 5. 

Each post contains various metadata (see :ref:`posts`) about the post. In this example we are interested in two things: the relative URL to the permalinked post as well as the title of the post. We create the anchor containing the relative URL ``${post.path}`` and we name the anchor the same as the post ``${post.title}``. The rendered HTML file will now look something like this::

  <html>
    <body>
      This is a header you want on every page
      <hr/>
       <div id="main_block">
        Here's the five most recent posts from the blog:
        <ul>
         <li><a href="/blog/2009/08/29/profit">Profit!</a></li>
         <li><a href="/blog/2009/08/29/halcyon-and-on-and-on">Halcyon and On and On</a></li>
         <li><a href="/blog/2009/08/29/were-on-a-roll">We're on a roll</a></li>
         <li><a href="/blog/2009/08/29/another-post">Another Post</a></li>
         <li><a href="/blog/2009/08/22/first-post">First Post!</a></li>
        </ul>
       </div>
      <hr/>
      This is a footer you want on every page
    </body>
  </html>

.. _required-templates:

Template Environment
--------------------

In the last section we introduced a special Blogofile object called ``bf``. This object is a gateway to all things related to Blogofile and is provided to all your templates.

You can also import it into your :ref:`Controllers` and :ref:`Filters`::

    import blogofile_bf as bf

Blogofile modules
+++++++++++++++++

``bf`` holds all of the core Blogofile modules, for example:
 * ``bf.util``
 * ``bf.config``
 * ``bf.writer``

Controller configuration
++++++++++++++++++++++++

``bf`` holds all the controller configuration, for example:

  * ``bf.controllers.blog.enabled``
  * ``bf.controllers.blog.path``

Filter configuration
++++++++++++++++++++

``bf`` holds all the filter configuration, for example:

  * ``bf.filters.syntax_highlight.enabled``
  * ``bf.filters.syntax_highlight.style``

Template context
++++++++++++++++

When a template is being rendered, it's sometimes useful to be able to maintain a context available throughout the time that a given template is being rendered. If, for example, you are rendering a template called ``my_cool_template.mako`` which inherits from ``site.mako`` and includes ``sidebar.mako``, a single context will be maintained that can be accessed from all three of those templates.

``bf.template_context`` is a `HierarchicalCache`_ object and is available inside any template and you can put whatever data you want on it. The one peice of information that is included by default is ``bf.template_context.template_name`` which records the original template requested to be rendered. In the above example, this would be ``my_cool_template.mako``.

.. _Mako: http://www.makotemplates.org

.. _great documentation: http://www.makotemplates.org/docs/

.. _inherrited: http://www.makotemplates.org/docs/inheritance.html

.. _included: http://www.makotemplates.org/docs/syntax.html#syntax_tags_include

.. _Mako syntax: http://www.makotemplates.org/docs/syntax.html#syntax_expression

.. _HierarchicalCache: http://github.com/EnigmaCurry/blogofile/blob/master/blogofile/cache.py#L22
