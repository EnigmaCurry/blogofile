import shutil
import os
from blogofile import util

from . import plugin

def copy_photos():
    plugin.logger.info("Copying gallery photos..")
    if plugin.config.gallery.src:
        #The user has supplied their own photos
        shutil.copytree(plugin.config.gallery.src,
                        util.fs_site_path_helper(
                "_site",plugin.config.gallery.path,"img"))
    else:
        #The user has not configured the photo path
        #Use the supplied photos as an example
        shutil.copytree(os.path.join(plugin.tools.get_src_dir(),"_photos"),
                        util.fs_site_path_helper(
                "_site",plugin.config.gallery.path,"img"))

def get_photo_names():
    img_dir = util.fs_site_path_helper(
        "_site",plugin.config.gallery.path,"img")
    return [p for p in os.listdir(img_dir) if p.lower().endswith(".jpg")]

def write_pages(photos):
    for photo in photos:
        plugin.tools.materialize_template(
            "photo.mako", (plugin.config.gallery.path,photo+".html"),
            {"photo":photo})

def write_index(photos):
    plugin.tools.materialize_template(
        "photo_index.mako", (plugin.config.gallery.path,"index.html"),
        {"photos":photos})
