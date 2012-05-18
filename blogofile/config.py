"""This loads the user's _config.py file and provides a standardized interface
into it."""

__author__ = "Ryan McGuire (ryan@enigmacurry.com)"

import os
import logging
import sys
import re

from . import util
import blogofile_bf as bf
from . import cache
from .cache import HierarchicalCache as HC
from . import controller
from . import plugin
from . import site_init
from . import filter as _filter

bf.config = sys.modules['blogofile.config']

logger = logging.getLogger("blogofile.writer")

class UnknownConfigSectionException(Exception):
    pass
class ConfigNotFoundException(Exception):
    pass

override_options = {} #override config options (mostly from unit tests)

#Default config sections
def reset_config():
    global site, controllers, filters, plugins, templates
    site = cache.HierarchicalCache()
    controllers = cache.HierarchicalCache()
    filters = cache.HierarchicalCache()
    plugins = cache.HierarchicalCache()
    templates = cache.HierarchicalCache()
reset_config()

def default_config_path():
    return os.path.join(os.path.split(site_init.__file__)[0], "_config.py")

with open(default_config_path()) as dc:
    default_config = dc.read()

def recompile():
    #Compile file_ignore_patterns
    import re
    global site
    site.compiled_file_ignore_patterns = []
    for p in site.file_ignore_patterns:
        if hasattr(p,"findall"):
            #probably already a compiled regex.
            site.compiled_file_ignore_patterns.append(p)
        else:
            site.compiled_file_ignore_patterns.append(
                re.compile(p, re.IGNORECASE))
        
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
    _filter.preload_filters()
    controller.load_controllers(namespace=bf.config.controllers)
    if path:
        with open(path) as pf:
            exec(compile(pf.read(), path, 'exec'))
    #config is now in locals() but needs to be in globals()
    for k, v in list(locals().items()):
        globals()[k] = v
    #Override any options (from unit tests)
    for k, v in list(override_options.items()):
        if "." in k:
            parts = k.split(".")
            cache_object = ".".join(parts[:-1])
            setting = parts[-1]
            cache_object = eval(cache_object)
            cache_object[setting] = v
        else:
            globals()[k] = v
    recompile()
    
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

def init_interactive(args=None):
    if args is None:
        args = cache.Cache()
        args.src_dir = os.curdir
    cache.reset_bf()
    try:
        # Always load the _config.py from the current directory.
        # We already changed to the directory specified with --src-dir
        init("_config.py")
    except ConfigNotFoundException:
        sys.stderr.write("No configuration found in source dir: {0}\n".format(args.src_dir))
        sys.stderr.write("Want to make a new site? Try `blogofile init`\n")
        sys.exit(1)
