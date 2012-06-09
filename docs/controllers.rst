.. _controllers:

Controllers
***********

Controllers are used when you want to create a whole chunk of your site dynamically everytime you compile your site. The best example of this is a blog. The whole purpose of a blog engine is to make it so you don't have to update 10 different things when you just want to make a post. Examples of controllers include:

* A sequence of blog posts listed in reverse chronological order paginated 5 posts per page.
* A blog post archiver to list blog posts in reverse chronological order listed by year and month.
* A blog post categorizer to list blog posts in reverse chronological order listed by category.
* An RSS/Atom feed generator for all posts, or for a single category.
* A permalink page for all blog posts.

All of these are pretty much a necessity for a blog engine, but none of these are included within the core of Blogofile itself. One of Blogofile's core principles is to remain light, configurable, and to make little assumption about how a user's site should behave. All of these blog specific tasks are relegated to a type of plugin system called controllers so that they can be tailored to each individual's tastes as well as leave room for entirely new types of controllers written by the user.

The simple_blog sources (which you can obtain by running ``blogofile init simple_blog``) include all of these controllers in the ``_controllers`` directory. But let's look at an even simpler example for the purposes of this tutorial.

.. _controller-simple-example:

A Simple Controller
-------------------

Suppose you wanted to create a simple photo gallery with a comments page for each photo. You don't want to have to create a new mako template for every picture you upload, so let's write a controller instead. The controller will be really simple: read all the photos in the photo directory and create a single page for each photo and allow comments on the photo using `Disqus`_. While we're at it, let's also create an index page listing all the photos with a thumbnail and the name of the image.

First create the controller called ``_controllers/photo_gallery.py``::

 # A stupid little photo gallery for Blogofile.

 # Read all the photos in the /photos directory and create a page for each along
 # with Disqus comments.
 
 import os
 from blogofile.cache import bf
 
 config = {"name"        : "Photo Gallery",
           "description" : "A very simplistic photo gallery, used as an example",
           "priority"    : 40.0}

 photos_dir = os.path.join("demo","photo_gallery")
 
 def run():
     photos = read_photos()
     write_pages(photos)
     write_photo_index(photos)
     
 def read_photos():
     #This could be a lot more advanced, like supporting subfolders, creating
     #thumbnails, and even reading the Jpeg EXIF data for better titles and such.
     #This is kept simple for demonstration purposes.
     return [p for p in os.listdir(photos_dir) if p.lower().endswith(".jpg")]
 
 def write_pages(photos):
     for photo in photos:
         bf.writer.materialize_template("photo.mako", 
                 (photos_dir,photo+".html"), {"photo":photo})
 
 def write_photo_index(photos):
     bf.writer.materialize_template("photo_index.mako", 
                 (photos_dir,"index.html"), {"photos":photos})
 
When a controller is loaded, the first thing Blogofile looks for is a ``run()`` method to invoke. It never takes any arguments, each controller is expected to know what it's going to do of it's own accord. 

In this example the ``run()`` method does all the work:

* It reads all the photos: ``read_photos()``
* It creates a page for each photo: ``write_pages()``
* It creates a single index page for all the photos: ``write_photo_index()``

The ``bf.writer.materialize_template`` method is provided to make it easy to pass data to a template and have it written to disk inside the ``_site`` directory.

The ``write_pages()`` method references a reusable template residing in ``_templates/photo.mako``::

 <%inherit file="site.mako" />
 <center><img src="/demo/photo_gallery/${photo}"/></center>
 <div id="disqus_thread"></div>
 <script type="text/javascript">
   var disqus_url = "${bf.config.site.url}/demo/photo_gallery/${photo}.html";
 </script>
 <script type="text/javascript" 
    src="http://disqus.com/forums/${bf.config.blog.disqus.name}/embed.js"></script>
 <noscript><a href="http://${bf.config.blog.disqus.name}.disqus.com/?url=ref">
     View the discussion thread.</a>
 </noscript><a href="http://disqus.com" class="dsq-brlink">blog comments powered by 
 <span class="logo-disqus">Disqus</span></a>
 
The controller passes in a single variable: ``photo``, which is the filename of the photo. In a more complete photo gallery, one might pass an object that held the EXIF data.

The ``write_photo_index()`` method references a reusable template residing in ``_templates/photo_index.mako``::

 <%inherit file="_templates/site.mako" /> 
 My Photos:
 <table>
 % for photo in photos:
   <tr><td><a href="${photo}.html">
     <img src="${photo}" height="175"></a></td><td>${photo}</td></tr>
 % endfor
 </table>

The controller passes a single variable: ``photos``, which is a sequence of all the photos filenames. In a more complete photo gallery, one might pass a sequence of objects that had references to the full jpg as well as a thumbnail and EXIF data.

This example is included in the `blogofile.com sources <http://www.github.com/EnigmaCurry/blogofile.com>`_ and can also `be viewed live <http://www.blogofile.com/demo/photo_gallery>`_.

Controller structure
--------------------

Controllers can be single .py files inside the _controllers directory, as in the photo gallery example above, or they can be full python modules (Python modules are directories with a ``__init__.py`` file). This second method will let you split your controller among multiple files.

Controllers are always disabled by default, and must be explicitly turned on in your ``_config.py``. For example, to enable the photo gallery example::

    controllers.photo_gallery.enabled = True

Controllers have a standardized configuration protocol. All controllers define a dictionary called ``config``. By default it contains the following values::

    config = {"name"        : None,
              "description" : None,
              "author"      : None,
              "url"         : None,
              "priority"    : 50.0,
              "enabled"     : False}

These settings are as follows:

 * name - The human friendly name for the controller.
 * author - The name or group responsible for writing the controller.
 * description - A brief description of what the controller does.
 * url - The URL where the controller can be downloaded on the author's site.
 * priority - The default priority to determine sequence of execution. This is optional, if not provided, it will default to 50. Controllers with higher priorities get run sooner than ones with lower priorities.

These are just the default settings, a controller author may provide as many configuration settings as he wants. 

A user can override any configuration setting in their ``_config.py``::

    controllers.photo_gallery.albums.photos_per_page = 5

Controller Initialization
-------------------------

Controller's have an additional optional method called ``init()``. Like the ``run()`` method, it doesn't take any arguments, it's expected that the controller knows how to initialize itself. The initialization is useful when you need to perform some preparation work before running the main controller. Typical use cases are where two controllers interact with each other and have cyclical dependencies on one another. With an initialization step, you can avoid chicken-or-the-egg problems between two controllers that require data from each other at runtime.

.. _Disqus: http://www.disqus.com

