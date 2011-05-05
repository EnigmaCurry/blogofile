import os

from blogofile.cache import bf

import blogofile_plugin_test as plugin

def init():
    #Any setup you need to do before running goes here.
    pass

def run():
    #Run the controller
    from . import photos
    photos.copy_photos()
    photo_files = photos.get_photo_names()
    photos.write_pages(photo_files)
    photos.write_index(photo_files)
    
