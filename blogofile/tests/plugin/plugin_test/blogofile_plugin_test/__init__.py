#!/usr/bin/env python
# -*- coding: utf-8 -*-    
import logging
import blogofile
import blogofile.plugin
from blogofile.cache import bf, HierarchicalCache as HC
try:
    import urllib.parse as urlparse
except ImportError:
    #Python 2
    import urlparse

from . import commands

## Configure the plugin meta information:
__dist__ = dict(
    #The name of your plugin:
    name = "Plugin Unit Tests",
    #The namespace of your plugin as used in _config.py.
    #referenced as bf.config.plugins.name
    config_name = "plugin_test",
    #Your name:
    author = "Ryan McGuire",
    #The version number:
    version = "0.1",
    #The URL for the plugin (where to download, documentation etc):
    url = "http://www.blogofile.com",
    #A one line description of your plugin presented to other Blogofile users:
    description = "Unit tests for plugins",
    #PyPI description, could be the same, except this text
    #should mention the fact that this is a Blogofile plugin
    #because non-Blogofile users will see this text:
    pypi_description = "Unit tests for blogofile plugins",
    #Command parser
    #Ths installs extra commands into blogofile, see commands.py
    command_parser_setup = commands.setup
    )

__version__ = __dist__["version"]

#This is your plugin's external configuration object.  Define all the
#default settings for your plugin that the user may override if they
#choose. Users can access/modify these settings in _config.py:
#
#     plugins.example.gallery.src = "/path/to/my/photos"
#
config = HC(
    base_template = "site.mako",
    gallery = HC(
        #The source directory containing photos
        src = None, #None means use the supplied photos
        #The path on the site to host the gallery
        path = "photos"
        )
    )

tools = blogofile.plugin.PluginTools(__name__)
logger = logging.getLogger("blogofile.plugins.{0}".format(__name__))

def init():
    #Initialize the controllers here, but we can reuse a generic tool for that:
    tools.initialize_controllers()
    #The base template is a configurable option, injected into the
    #template rendrer here at runtime:
    tools.template_lookup.put_template(
        "plugin_base_template",tools.template_lookup.get_template(
            config.base_template))

def run():
    #Run the controllers here, but we can reuse a generic tool for that too:
    tools.run_controllers()
