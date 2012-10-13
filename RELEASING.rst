Releasing Blogofile
*******************

Checklist for doing a release of Blogofile and the blogifile_blog plugin.

* Do a platform test via tox::

    $ tox -r

* Ensure that all features of the release are documented (audit CHANGES.txt).

* Ensure that the docs build::

    $ cd docs
    $ make clean html

* Write a release post for blogofile.com.

* Change version number in:

  * Blogofile:

    * blogofile/__init__.py
    * docs/conf.py
    * CHANGES.txt

  * blogofile_blog:

    * blogofile_blog/__init__.py

  * blogofile.com:

    * _config.py

* Test upload to PyPI::

    $ python setup.py sdist register -r testpypi upload -r testpypi

  for both Blogofile and blogofile_blog.

* Test installation in a pristine virtualenv::

    $ virtualenv --python=python3.2 blogofile-testrel
    $ cd blogofile-testrel
    $ source bin/activate
    $ pip install --extra-index-url http://testpypi.python.org/pypi \
          "Blogofile==<version>"
    $ pip install --extra-index-url http://testpypi.python.org/pypi \
          "blogofile_blog==<version>"

  and then test building a site, even if it's the sample blog via::

    $ blogofile init test_blog blog
    $ blogofile build -s test_blog

* Create release tags in Blogofile and blogofile_blog repos.

* Release to PyPI::

    $ python setup.py sdist register upload

  for both Blogofile and blogofile_blog.

* Publish the release post for blogofile.com::

    $ git push publish

* Announce to blogofile-discuss group/maillist.

* Annouce to Google+.

* Announce to Twitter.
