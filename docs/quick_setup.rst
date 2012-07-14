A Quick Tutorial
****************

.. note::
   This documents the 0.8 development version of Blogofile_
   (also known as the *plugins* branch).
   There are also `docs for 0.7.1`_, the current stable release.

.. _Blogofile: http://blogofile.com/
.. _docs for 0.7.1: http://blogofile.readthedocs.org/en/0.7.1docs/

Ok, if you're impatient, this is the short *short* [#f1]_ version of
getting setup with blogofile.

* Install Blogofile and the blogofile_blog plugin,
  (see :ref:`install-blogofile`).
  Use a Python virtualenv_ or :command:`sudo` as you wish.

  ::

    git clone git://github.com/EnigmaCurry/blogofile.git
    git clone git://github.com/EnigmaCurry/blogofile_blog.git
    cd blogofile
    python setup.py install
    cd ../blogofile_blog
    python setup.py install

  .. _virtualenv: http://www.virtualenv.org/

* Initialize a blog site in a directory call :file:`mysite`::

    blogofile init mysite blog

* Build the site::

    blogofile build -s mysite

* Serve the site::

    blogofile serve -s mysite

* Open your web browser to http://localhost:8080 to see the rendered site.

* Explore the :command:`blogofile` commands with :command:`blogofile help`.

* Create some post files in the :file:`_posts` directory (see :ref:`posts`)

The next chapters explain this process in more detail.

.. rubric:: Footnotes

.. [#f1] * **Priest**: Do you?

 * **Vespa**: Yes.

 * **Priest**: Do *you*?

 * **Lone Star**: I do.

 * **Priest**: Good! Fine! You're married! Kiss Her!

.. _git: http://www.git-scm.org
