Blogofile is a static website compiler that lets you use various template
libraries (Mako, Jinja2),
and various markup languages (reStructuredText, Markdown, Textile)
to create sites that can be served from any web server you like.

Version 0.8 of Blogofile breaks out the core static site compiler
and gives it a plugin interface.
That allows features like the blog engine that was Blogofile's
original raison d`être to be built on top of the core.

`blogofile_blog`_ is a blog engine plugin created by the Blogofile developers.
With it installed you get a simple blog engine that requires no
database and no special hosting environment.
You customize a set of Mako templates,
create posts in reStructuredText, Markdown, or Textile, (or even plain HTML)
and blogofile generates your entire blog as
plain HTML, CSS, images, and Atom/RSS feeds
which you can then upload to any old web server you like.
No CGI or scripting environment is needed on the server.

See the `Blogofile website`_ for an example of a Blogofile-generated
site that includes a blog,
and check out the `project docs`_ for a quick-start guide,
and detailed usage instructions.

Or, if you're the "just get it done sort",
create a virtualenv,
and dive in with::

  pip install -U Blogofile
  pip install -U blogofile_blog

.. _blogofile_blog: http://pypi.python.org/pypi/blogofile_blog/
.. _Blogofile website: http://www.blogofile.com/
.. _project docs: http://blogofile.readthedocs.org/en/latest/
