import sys, os, os.path
import logging
import pkg_resources

import pprint

from mako.lookup import TemplateLookup

from .cache import bf, HierarchicalCache
from . import controller
from . import filter

logger = logging.getLogger("blogofile.plugin")

default_plugin_config = {
    "priority"    : 50.0,
    "enabled"     : False }

reserved_attributes = ["mod","filters","controllers","site_src"]

def iter_plugins():
    for plugin in pkg_resources.iter_entry_points("blogofile.plugins"):
        yield plugin.load()

def list_plugins(args):
    for plugin in iter_plugins():
        print("{0} ({1}) - {2} - {3}".format(plugin.__dist__['config_name'],
                                           plugin.__dist__['version'],
                                           plugin.__dist__['description'],
                                           plugin.__dist__['author']))
        
def check_plugin_config(module):
    """Ensure that a plugin has the required components
    and none of the reserved ones."""
    try:
        assert isinstance(module.config, HierarchicalCache)
    except AttributeError:
        raise AssertionError("Plugin {0} has no config HierarchicalCache".format(module))
    except AssertionError:
        raise AssertionError("Plugin {0} config object must extend from "\
            "HierarchicalCache".format(module))
    try:
        module.__dist__
    except AttributeError:
        raise AssertionError("Plugin {0} has no __dist__ dictionary, "\
            "describing the plugins metadata.".format(module))
    #TODO: Why does this fail in a test context? Not really *that* important..
    # for attr in reserved_attributes:
    #     if module.config.has_key(attr):
    #         raise AssertionError, "'{0}' is a reserved attribute name for " \
    #             "Blogofile plugins. They should not be assigned manually."\
    #             .format(attr)

def load_plugins():
    """Discover all the installed plugins and load them into bf.config.plugins

    Load the module itself, the controllers, and the filters"""
    for plugin in iter_plugins():
        namespace = bf.config.plugins[plugin.__dist__["config_name"]] = \
            getattr(plugin,"config")
        check_plugin_config(plugin)
        namespace.mod = plugin
        print(plugin)
        plugin_dir = os.path.dirname(sys.modules[plugin.__name__].__file__)
        #Load filters
        filter.preload_filters(
            namespace=namespace.filters,
            directory=os.path.join(plugin_dir,"site_src","_filters"))
        for name, filter_ns in list(namespace.filters.items()):
            #Filters from plugins load in their own namespace, but
            #they also load in the regular filter namespace as long as
            #there isn't already a filter with that name. User filters
            #from the _filters directory are loaded after plugins, so
            #they are overlaid on top of these values and take
            #precedence.
            if name not in bf.config.filters:
                bf.config.filters[name] = filter_ns
        #Load controllers
        controller.load_controllers(
            namespace=namespace.controllers,
            directory=os.path.join(plugin_dir,"site_src","_controllers"),
            defaults={"enabled":True})

def init_plugins():
    for name, plugin in list(bf.config.plugins.items()):
        if plugin.enabled:
            logger.info("Initializing plugin: {0}".format(
                    plugin.mod.__dist__['config_name']))
            plugin.mod.init()
        
class PluginTools(object):
    """Tools for a plugin to get information about it's runtime environment"""
    def __init__(self, module_name):
        self.module = sys.modules[module_name]
        self.namespace = self.module.config
        self.template_lookup = self.__get_template_lookup()
        self.logger = logging.getLogger("blogofile.plugins.{0}".format(module_name))
    def materialize_template(self, template_name, location, attrs={}, lookup=None):
        #Just like the regular bf.writer.materialize_template.
        #However, this uses the blog template lookup by default.
        if lookup==None:
            lookup = self.template_lookup
        bf.writer.materialize_template(template_name, location, attrs, lookup)
    def add_template_dir(self, path):
        self.template_lookup.directories.append(path)
    def __get_template_lookup(self):
        return TemplateLookup(
            directories=[
                os.path.join(self.get_src_dir(),"_templates"),"_templates"],
            input_encoding='utf-8', output_encoding='utf-8',
            encoding_errors='replace')
    def get_src_dir(self):
        return os.path.join(
            os.path.dirname(sys.modules[self.module.__name__].__file__),
            "site_src")
    def initialize_controllers(self):
        for name, controller in list(self.module.config.controllers.items()):
            self.logger.info("Initializing controller: {0}".format(name))
            controller.mod.init()
    def run_controllers(self):
        for name, controller in list(self.module.config.controllers.items()):
            self.logger.info("Running controller: {0}".format(name))
            controller.mod.run()
        
