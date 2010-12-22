################################################################################
## Controllers
##
## Blogofile controllers reside in the user's _controllers directory
## and can generate content for a site.
##
## Controllers can either be standalone .py files, or they can be modules.
##
## Every controller has a contract to provide the following:
##  * a run() method, which accepts no arguments.
##  * A dictionary called "config" containing the following information:
##    * name - The human friendly name for the controller.
##    * author - The name or group responsible for writing the controller.
##    * description - A brief description of what the controller does.
##    * url - The URL where the controller is hosted.
##    * priority - The default priority to determine sequence of execution
##       This is optional, if not provided, it will default to 50.
##       Controllers with higher priorities get run sooner than ones with
##       lower priorities.
##
## Example controller (either a standalone .py file or
##                       __init__.py inside a module):
##
##     config = {"name"        : "My Controller",
##               "description" : "Does cool stuff",
##               "author"      : "Joe Programmer",
##               "url"         : "http://www.yoururl.com/my-controller",
##               "priority"    : 90.0}
## 
##     def run():
##         do_whatever_it_needs_to()
##
## Users can configure a controller in _config.py:
##
##   #To enable the controller (default is always disabled):
##   controller.name_of_controller.enabled = True
##
##   #To set the priority:
##   controllers.name_of_controller.priority = 40
##
##   #To set a controller specific setting:
##   controllers.name_of_controller.nifty_setting = "whatever"
##
## Settings set in _config.py always override any default configuration
## for the controller.
##
## TODO: implement this :)
##
################################################################################
import sys
import os
import operator
import logging

from cache import bf

logger = logging.getLogger("blogofile.controller")

__loaded_controllers = {} #name -> module

default_controller_config = {"name"        : None,
                             "description" : None,
                             "author"      : None,
                             "url"         : None,
                             "priority"    : 50.0,
                             "enabled"     : False}


#TODO: seems almost identical to filters.preload_filters; commonize
def __find_controller_names(directory="_controllers"):
    if(not os.path.isdir(directory)): #pragma: no cover
        return
    #Find all the standalone .py files and modules in the _controllers dir
    for fn in os.listdir(directory):
        p = os.path.join(directory, fn)
        if os.path.isfile(p):
            if fn.endswith(".py"):
                yield fn[:-3]
        elif os.path.isdir(p):
            if os.path.isfile(os.path.join(p, "__init__.py")):
                yield fn


#TODO: seems almost identical to filters.init_filters; commonize
def init_controllers():
    """Controllers have an optional init method that runs before the run
    method"""
    for controller in sorted(bf.config.controllers.values(),
            key=operator.attrgetter("priority")):
        try:
            if "mod" in controller:
                if type(controller.mod).__name__ == "module":
                    controller.mod.init()
        except AttributeError:
            pass


# TODO: seems almost identical to filters.load_filter; commonize
def load_controller(name, directory="_controllers"):
    """Load a single controller by name"""
    #Don't generate pyc files in the _controllers directory
    #Reset the original sys.dont_write_bytecode setting where we're done
    try:
        return __loaded_controllers[name]
    except KeyError:
        pass
    try:
        initial_dont_write_bytecode = sys.dont_write_bytecode
    except KeyError:
        initial_dont_write_bytecode = False
    try:
        sys.path.insert(0, directory)
        logger.debug("loading controller: {0}".format(name))
        try:
            sys.dont_write_bytecode = True
            controller = __import__(name)
        except (ImportError,),e:
            logger.error(
                "Cannot import controller : {0} ({1})".format(name, e))
            raise
        # Remember the actual imported module
        bf.config.controllers[name].mod = controller
        # Load the blogofile defaults for controllers:
        for k, v in default_controller_config.items():
            bf.config.controllers[name][k] = v
        # Load any of the controller defined defaults:
        try:
            controller_config = getattr(controller, "config")
            for k, v in controller_config.items():
                if k != "enabled":
                    if "." in k:
                        #This is a hierarchical setting
                        tail = bf.config.controllers[name]
                        parts = k.split(".")
                        for part in parts[:-1]:
                            tail = tail[part]
                        tail[parts[-1]] = v
                    else:
                        bf.config.controllers[name][k] = v
        except AttributeError:
            pass
        #Provide every controller with a logger:
        c_logger = logging.getLogger("blogofile.controllers." + name)
        bf.config.controllers[name]["logger"] = c_logger
        return bf.config.controllers[name].mod
    finally:
        sys.path.remove("_controllers")
        sys.dont_write_bytecode = initial_dont_write_bytecode
    
        
def load_controllers(directory="_controllers"):
    """Find all the controllers in the _controllers directory
    and import them into the bf context"""
    for name in __find_controller_names():
        load_controller(name, directory)


def defined_controllers(namespace=bf, only_enabled=True):
    """Find all the enabled controllers in order of priority

    if only_enabled == False, find all controllers, regardless of
    their enabled status

    >>> bf_test = bf.cache.HierarchicalCache()
    >>> bf_test.config.controllers.one.enabled = True
    >>> bf_test.config.controllers.one.priority = 30
    >>> bf_test.config.controllers.two.enabled = False
    >>> bf_test.config.controllers.two.priority = 90
    >>> bf_test.config.controllers.three.enabled = True #default priority 50
    >>> defined_controllers(bf_test)
    ['three', 'one']
    >>> defined_controllers(bf_test, only_enabled=False)
    ['two', 'three', 'one']
    """
    controller_priorities = [] # [(controller_name, priority),...]
    for name, settings in namespace.config.controllers.items():
        #Get only the ones that are enabled:
        c = namespace.config.controllers[name]
        if "enabled" not in c or c['enabled'] == False:
            #The controller is disabled
            if only_enabled:
                continue
        #Get the priority:
        if "priority" in c:
            priority = c['priority']
        else:
            priority = c['priority'] = 50
        controller_priorities.append((name, priority))
    #Sort the controllers by priority
    return [x[0] for x in sorted(controller_priorities,
                                 key=operator.itemgetter(1),
                                 reverse=True)]

def run_all():
    """Run each controller in priority order"""
    #Get the controllers in priority order:
    controller_names = defined_controllers()
    #Temporarily add _controllers directory onto sys.path
    for name in controller_names:
        controller = bf.config.controllers[name].mod
        if "run" in dir(controller):
            logger.info("running controller: {0}".format(name))
            controller.run()
        else:
            logger.debug(
                "controller {0} has no run() method, skipping it.".format(name))
