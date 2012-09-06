# -*- coding: utf-8 -*-
from __future__ import print_function
import logging
import os
import os.path
import pkg_resources
import sys
from mako.lookup import TemplateLookup
import six
from . import controller
from . import filter as _filter
from . import template
from .cache import bf
from .cache import HierarchicalCache


logger = logging.getLogger("blogofile.plugin")

default_plugin_config = {
    "priority": 50.0,
    "enabled": False,
    }

reserved_attributes = ["mod", "filters", "controllers", "site_src"]


def iter_plugins():
    for plugin in pkg_resources.iter_entry_points("blogofile.plugins"):
        yield plugin.load()


def get_by_name(name):
    for plugin in iter_plugins():
        if plugin.__dist__['config_name'] == name:
            return plugin


def list_plugins(args):
    for plugin in iter_plugins():
        print("{0} ({1}) - {2} - {3}".format(plugin.__dist__['config_name'],
                                             plugin.__dist__['version'],
                                             plugin.__dist__['description'],
                                             plugin.__dist__['author']))


def check_plugin_config(module):
    """Ensure that a plugin has the required components
    and none of the reserved ones.
    """
    try:
        assert isinstance(module.config, HierarchicalCache)
    except AttributeError:
        raise AssertionError("Plugin {0} has no config HierarchicalCache"
                             .format(module))
    except AssertionError:
        raise AssertionError("Plugin {0} config object must extend from "
                             "HierarchicalCache".format(module))
    try:
        module.__dist__
    except AttributeError:
        raise AssertionError("Plugin {0} has no __dist__ dictionary, "
                             "describing the plugins metadata.".format(module))
    #TODO: Why does this fail in a test context? Not really *that* important..
    # for attr in reserved_attributes:
    #     if module.config.has_key(attr):
    #         raise AssertionError, "'{0}' is a reserved attribute name for " \
    #             "Blogofile plugins. They should not be assigned manually."\
    #             .format(attr)


def load_plugins():
    """Discover all the installed plugins and load them into bf.config.plugins

    Load the module itself, the controllers, and the filters.
    """
    for plugin in iter_plugins():
        namespace = bf.config.plugins[plugin.__dist__["config_name"]] = \
            getattr(plugin, "config")
        check_plugin_config(plugin)
        namespace.mod = plugin
        plugin_dir = os.path.dirname(sys.modules[plugin.__name__].__file__)
        # Load filters
        _filter.preload_filters(
            namespace=namespace.filters,
            directory=os.path.join(plugin_dir, "site_src", "_filters"))
        # Load controllers
        controller.load_controllers(
            namespace=namespace.controllers,
            directory=os.path.join(plugin_dir, "site_src", "_controllers"),
            defaults={"enabled": True})


def init_plugins():
    for name, plugin in list(bf.config.plugins.items()):
        if plugin.enabled:
            if "mod" not in plugin:
                print("Cannot find requested plugin: {0}".format(name))
                print("Build aborted.")
                sys.exit(1)
            logger.info("Initializing plugin: {0}".format(
                    plugin.mod.__dist__['config_name']))
            plugin.mod.init()
            for name, filter_ns in list(plugin.filters.items()):
                # Filters from plugins load in their own namespace, but
                # they also load in the regular filter namespace as long as
                # there isn't already a filter with that name. User filters
                # from the _filters directory are loaded after plugins, so
                # they are overlaid on top of these values and take
                # precedence.
                if name not in bf.config.filters:
                    bf.config.filters[name] = filter_ns
                elif "mod" not in bf.config.filters[name]:
                    filter_ns.update(bf.config.filters[name])
                    bf.config.filters[name] = filter_ns


class PluginTools(object):
    """Tools for a plugin to get information about it's runtime environment.
    """
    def __init__(self, module):
        self.module = module
        self.namespace = self.module.config
        self.template_lookup = self._template_lookup()
        self.logger = logging.getLogger(
            "blogofile.plugins.{0}".format(self.module.__name__))

    def _template_lookup(self):
        return TemplateLookup(
            directories=[
                "_templates", os.path.join(self.get_src_dir(), "_templates")],
            input_encoding='utf-8', output_encoding='utf-8',
            encoding_errors='replace')

    def get_src_dir(self):
        """Return the plugin's :file:`site_src directory path.

        :returns: :file:`site_src` path for the plugin.
        :rtype: str
        """
        return os.path.join(os.path.dirname(self.module.__file__), "site_src")

    def materialize_template(self, template_name, location, attrs={}):
        """Materialize a template using the plugin's TemplateLookup
        instance.

        :arg template_name: File name of the template to materialize.
        :type template_name: str

        :arg location: Path and file name in the :file:`_site`
                       directory to render the template to.
        :type location: str

        :arg attrs: Template variable names and values that will be
                    used as the data context to render the template
                    with.
        :type attrs: dict
        """
        template.materialize_template(
            template_name, location, attrs=attrs,
            lookup=self.template_lookup, caller=self.module)

    def add_template_dir(self, path, append=True):
        """Add a template directory to the plugin's TemplateLookup
        instance directories list.

        :arg path: Template path to add to directories list.
        :type path: str

        :arg append: Add the template path to the end of the
                     directories list when True (the default),
                     otherwise, add it to the beginning of the list.
        :type append: Boolean
        """
        if append:
            self.template_lookup.directories.append(path)
        else:
            self.template_lookup.directories.insert(0, path)

    def initialize_controllers(self):
        """Initialize the plugin's controllers.
        """
        for name, controller in six.iteritems(self.module.config.controllers):
            self.logger.info("Initializing controller: {0}".format(name))
            controller.mod.init()

    def run_controllers(self):
        """Run the plugin's controllers.
        """
        for name, controller in six.iteritems(self.module.config.controllers):
            self.logger.info("Running controller: {0}".format(name))
            controller.mod.run()
