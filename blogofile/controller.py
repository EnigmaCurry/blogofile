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
import imp
import logging

from cache import bf

logger = logging.getLogger("blogofile.controller")

default_controller_config = {"name"        : "None",
                             "description" : "None",
                             "author"      : "None",
                             "url"         : "None",
                             "priority"    : 50.0,
                             "enabled"     : False}



def __find_controller_names(directory="_controllers"):
    if(not os.path.isdir("_controllers")): #pragma: no cover
            return
    #Find all the standalone .py files and modules in the _controllers dir
    for fn in os.listdir(directory):
        p = os.path.join(directory,fn)
        if os.path.isfile(p):
            if fn.endswith(".py"):
                yield fn.rstrip(".py")
        elif os.path.isdir(p):
            if os.path.isfile(os.path.join(p,"__init__.py")):
                yield fn

def load_controllers(directory="_controllers"):
    """Find all the controllers in the _controllers directory
    and import them into the bf context"""
    try:
        sys.path.insert(0, "_controllers")
        for module in __find_controller_names():
            try:
                controller = __import__(module)
                print controller
            except ImportError:
                logger.warn(
                    "cannot find controller referenced in _config.py : %s" %
                            name)
                continue
            # Remember the actual imported module
            bf.config.controllers[module].mod = controller
            # Load the blogofile defaults for controllers:
            for k, v in default_controller_config.items():
                bf.config.controllers[module][k] = v
            # Load any of the controller defined defaults:
            try:
                controller_config = getattr(controller,"default_config")
                for k,v in controller_config.items():
                    if k != "enabled":
                        bf.config.controllers[module][k] = v
            except AttributeError:
                pass
    finally:
        sys.path.remove("_controllers")

def defined_controllers(only_enabled=True):
    """Find all the enabled controllers in order of priority

    if only_enabled == False, find all controllers, regardless of
    their enabled status
    
    >>> bf.config.controllers.one.enabled = True
    >>> bf.config.controllers.one.priority = 30
    >>> bf.config.controllers.two.enabled = False
    >>> bf.config.controllers.two.priority = 90
    >>> bf.config.controllers.three.enabled = True #default priority 50
    >>> defined_controllers()
    ['three', 'one']
    >>> defined_controllers(only_enabled=False)
    ['two', 'three', 'one']
    """
    controller_priorities = [] # [(controller_name, priority),...]
    for name, settings in bf.config.controllers.items():
        #Get only the ones that are enabled:
        c = bf.config.controllers[name]
        if (not c.has_key("enabled")) or c['enabled'] == False:
            #The controller is disabled
            if only_enabled: continue
        #Get the priority:
        if c.has_key("priority"):
            priority = c['priority']
        else:
            priority = c['priority'] = 50
        controller_priorities.append((name,priority))
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
            logger.info("running controller: %s" % name)
            controller.run()
        else:
            logger.debug("controller %s has no run() method, skipping it." %
                         name)

def run_legacy_controllers():
    #TODO: not needed, for reference only
    if(not os.path.isdir("_controllers")): #pragma: no cover
            return 
    for py_file in [p for p in sorted(os.listdir("_controllers")) if
                    p.endswith(".py")]:
        controller_name = (py_file.split(".")[0].replace("-","_"))
        import_name = "controller_mod_"+controller_name
        mod = imp.load_source(import_name,util.path_join("_controllers",py_file))
        setattr(self.bf.controllers,controller_name,mod)
    for py_file in [p for p in sorted(os.listdir("_controllers")) if
                    p.endswith(".py")]:
        logger.info("Running controller: "+py_file)
        controller_name = (py_file.split(".")[0].replace("-","_"))
        mod = getattr(self.bf.controllers,controller_name)
        if "run" in dir(mod):
            mod.run()
        else:
            logger.debug("Controller %s has no run() function, skipping it." % py_file)
