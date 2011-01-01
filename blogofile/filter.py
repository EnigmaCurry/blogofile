import sys
import os
import logging

import util

logger = logging.getLogger("blogofile.filter")

from cache import bf
bf.filter = sys.modules['blogofile.filter']

__loaded_filters = {} #name -> mod

default_filter_config = {"name"        : None,
                         "description" : None,
                         "author"      : None,
                         "url"         : None}


def run_chain(chain, content):
    """Run content through a filter chain.

    Works with either a string or a sequence of filters"""
    if chain is None: #pragma: no cover
        return content
    if not hasattr(chain, '__iter__'):
        #Not a sequence, must be a string, parse it
        chain = parse_chain(chain)
    for fn in chain:
        f = load_filter(fn)
        logger.debug("Applying filter: " + fn)
        content = f.run(content)
    logger.debug("Content: " + content)
    return util.force_unicode(content)


def parse_chain(chain):
    """Parse a filter chain into a sequence of filters"""
    parts = []
    for p in chain.split(","):
        p = p.strip()
        if p.lower() == "none":
            continue
        if len(p) > 0:
            parts.append(p)
    return parts


#TODO: seems almost identical to controllers.__find_controller_names; commonize
def preload_filters(directory="_filters"):
    #Find all the standalone .py files and modules
    #in the _filters dir and load them into bf
    if(not os.path.isdir(directory)): #pragma: no cover
        return
    for fn in os.listdir(directory):
        p = os.path.join(directory,fn)
        if os.path.isfile(p):
            if fn.endswith(".py"):
                load_filter(fn[:-3])
        elif os.path.isdir(p):
            if os.path.isfile(os.path.join(p, "__init__.py")):
                load_filter(fn)


#TODO: seems almost identical to controllers.init_controllers; commonize
def init_filters():
    """Filters have an optional init method that runs before the site is 
    built"""
    for filt in bf.config.filters.values():
        if "mod" in filt:
            try:
                filt.mod.init()
            except AttributeError:
                pass


#TODO: seems almost identical to controllers.load_controller; commonize
def load_filter(name):
    """Load a filter from the site's _filters directory"""
    logger.debug("Loading filter: " + name)
    #Don't generate pyc files in the _filters directory
    #Reset the original sys.dont_write_bytecode setting where we're done
    try:
        initial_dont_write_bytecode = sys.dont_write_bytecode
    except KeyError:
        initial_dont_write_bytecode = False
    #Return the cached filter, or load it from scratch it not cached.
    try:
        return __loaded_filters[name]
    except KeyError:
        try:
            sys.path.insert(0, "_filters")
            #Don't generate .pyc files in the _filters directory
            sys.dont_write_bytecode = True
            mod = __loaded_filters[name] = __import__(name)
            #Load the module into the bf context
            bf.config.filters[name].mod = mod
            #If the filter has any aliases, load those as well
            try:
                for alias in mod.config['aliases']:
                    __loaded_filters[alias] = mod
                    bf.config.filters[alias] = bf.config.filters[name]
            except:
                pass
            #Load the default blogofile config for filters:
            for k, v in default_filter_config.items():
                bf.config.filters[name][k] = v
            #Load any filter defined defaults:
            try:
                filter_config = getattr(mod, "config")
                for k, v in filter_config.items():
                    if "." in k:
                        #This is a hierarchical setting
                        tail = bf.config.filters[name]
                        parts = k.split(".")
                        for part in parts[:-1]:
                            tail = tail[part]
                        tail[parts[-1]] = v
                    else:
                        bf.config.filters[name][k] = v
            except AttributeError:
                pass
            return mod
        except: #pragma: no cover
            logger.error("Cannot load filter: "+name)
            raise
        finally:
            sys.path.remove("_filters")
            sys.dont_write_bytecode = initial_dont_write_bytecode
