A Quick Tutorial
****************

Ok, if you're impatient, this is the short *short* [#f1]_ version of getting setup with blogofile.

* Install Blogofile, (see :ref:`install-blogofile`):

 ``sudo easy_install blogofile``

* In a clean directory, initialize the bare bones sample site:

 ``blogofile init simple_blog``

* Or, for a more complete sample blog (requires git_):

 ``blogofile init blogofile.com``

* Create some post files in the _posts directory. (see :ref:`posts`)

* Build the site:

 ``blogofile build``

* Serve the site:

 ``blogofile serve 8080``

* Open your web browser to `http://localhost:8080 <http://localhost:8080>`_ to see the rendered site.

The next chapters explain this process in more detail.

.. rubric:: Footnotes

.. [#f1] * **Priest**: Do you?

 * **Vespa**: Yes.

 * **Priest**: Do *you*?

 * **Lone Star**: I do.

 * **Priest**: Good! Fine! You're married! Kiss Her!

.. _git: http://www.git-scm.org
