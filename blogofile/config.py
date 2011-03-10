#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This loads the user's _config.py file and provides a standardized interface
into it."""

__author__ = "Ryan McGuire (ryan@enigmacurry.com)"
__date__   = "Tue Jul 28 20:40:29 2009"

import os
import logging
import sys

import util
import writer
import blogofile_bf as bf
import cache
import controller
import plugin
import site_init
import filter

bf.config = sys.modules['blogofile.config']

logger = logging.getLogger("blogofile.writer")

__loaded = False

class UnknownConfigSectionException(Exception):
    pass
class ConfigNotFoundException(Exception):
    pass

override_options = {} #override config options (mostly from unit tests)

#Default config sections
site = cache.HierarchicalCache()
controllers = cache.HierarchicalCache()
filters = cache.HierarchicalCache()
plugins = cache.HierarchicalCache()

def default_config_path():
    return os.path.join(os.path.split(site_init.__file__)[0], "_config.py")

default_config = open(default_config_path()).read()

def recompile():
    #Compile file_ignore_patterns
    import re
    global site
    site.compiled_file_ignore_patterns = []
    for p in site.file_ignore_patterns:
        if isinstance(p, basestring):
            site.compiled_file_ignore_patterns.append(
                re.compile(p, re.IGNORECASE))
        else:
            #p could just be a pre-compiled regex
            site.compiled_file_ignore_patterns.append(p)
        
def __load_config(path=None):
    #Strategy:
    # 1) Load the default config
    # 2) Load the plugins
    # 3) Load the site filters and controllers
    # 4) Load the user's config.
    # This will ensure that we have good default values if the user's
    # config is missing something.
    exec(default_config)
    plugin.load_plugins()
    filter.preload_filters()
    controller.load_controllers(namespace=bf.config.controllers)
    if path:
        execfile(path)
    #config is now in locals() but needs to be in globals()
    for k, v in locals().items():
        globals()[k] = v
    #Override any options (from unit tests)
    for k, v in override_options.items():
        if "." in k:
            parts = k.split(".")
            cache_object = ".".join(parts[:-1])
            setting = parts[-1]
            cache_object = eval(cache_object)
            cache_object[setting] = v
        else:
            globals()[k] = v
    recompile()
    __loaded = True
    
def init(config_file_path=None):
    #Initialize the config, if config_file_path is None,
    #just load the default config
    logger.info("Loading config file : {0}".format(config_file_path))
    if config_file_path:
        if not os.path.isfile(config_file_path):
            raise ConfigNotFoundException
        __load_config(config_file_path)
    else:
        __load_config()
    return globals()['__name__']
