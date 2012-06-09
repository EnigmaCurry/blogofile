.. _vcs-integration:

Integration with Version Control
********************************

You Want Version Control
-------------------------------

You might not know it yet, but you want your blog under a `Version Control System <http://en.wikipedia.org/wiki/Version_Control>`_ (VCS). Consider the benefits:

* Regular and complete backups occur whenever you push your changes to another server.
* The ability to bring back any version of your site (or any single page) from history.
* The ability to work from any computer, without getting worried if you're working on the latest version or not.
* Automatic Deployment.

Automatic what? Even if you're a veteran to VCS, you may not realize that a VCS can do a lot more for you than just provide a place for you to dump your files. You can have your favorite VCS build and deploy your Blogofile based site for you everytime you commit new changes.

So why are you procrastinating? Get `git`_.

Automatic Deployment in Git
---------------------------

You need to have the origin server (the place that you 'git push' to) be the same server that hosts your website for this example to work. [#f1]_

On the server, checkout the project::

 git clone /path/to/your_repo.git /path/to/checkout_place

Create a new ``post-recieve`` hook in your git repo by creating the file ``/path/to/your_repo.git/hooks/post-receive``::

 #!/bin/sh

 #Rebuild the blog
 unset GIT_DIR
 cd /path/to/checkout_place
 git pull
 blogofile build

Configure your webserver to host your website out of ``/path/to/checkout_place/_site``.

Now whenever you ``git push`` to your webhost, your webserver should get automatically rebuilt. If Blogofile outputs any errors, you'll see them on your screen.

Other VCS solutions
-------------------

Most VCS should have support for a post recieve hook. If you create something cool in your own VCS of choice, let the `blogofile discussion group <http://groups.google.com/group/blogofile-discuss>`_ know and we'll add it to this document.

OJ wrote up how to do `something similar with mercurial <http://groups.google.com/group/blogofile-discuss/browse_frm/thread/e03f942b3655218e>`_.

.. rubric:: Footnotes

.. [#f1] If you deploy to a different server than the one hosting your git repository, you could just craft your own rsync or FTP command and put it at the bottom of the post-receive hook to deploy somewhere else. But that's beyond the scope of this document.

.. _git: http://www.git-scm.com
