#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
writer.py writes out the static blog to ./_site based on templates found in the
current working directory.
"""

__author__ = "Ryan McGuire (ryan@enigmacurry.com)"
__date__   = "Tue Feb  3 12:50:17 2009"

import logging
import os
import shutil

from mako.template import Template
from mako.lookup import TemplateLookup
from mako import exceptions as mako_exceptions

import util
import config
import cache
import filter
import controller
import plugin

logger = logging.getLogger("blogofile.writer")

class Writer(object):

    def __init__(self, output_dir):
        self.config = config
        #Base templates are templates (usually in ./_templates) that are only
        #referenced by other templates.
        self.base_template_dir = util.path_join(".", "_templates")
        self.output_dir = output_dir
        self.template_lookup = TemplateLookup(
                directories=[".", self.base_template_dir],
                input_encoding='utf-8', output_encoding='utf-8',
                encoding_errors='replace')

    def __load_bf_cache(self):
        #Template cache object, used to transfer state to/from each template:
        self.bf = cache.bf
        self.bf.writer = self
        self.bf.logger = logger
            
    def write_site(self):
        self.__setup_output_dir()
        self.__load_bf_cache()
        self.__init_plugins()
        self.__init_filters_controllers()
        self.__run_controllers()
        self.__write_files()
            
    def __setup_output_dir(self):
        """Setup the staging directory"""
        if os.path.isdir(self.output_dir): #pragma: no cover
            # I *would* just shutil.rmtree the whole thing and recreate it,
            # but I want the output_dir to retain its same inode on the
            # filesystem to be compatible with some HTTP servers.
            # So this just deletes the *contents* of output_dir
            for f in os.listdir(self.output_dir):
                f = util.path_join(self.output_dir, f)
                try:
                    os.remove(f)
                except OSError:
                    pass
                try:
                    shutil.rmtree(f)
                except OSError:
                    pass
        util.mkdir(self.output_dir)
            
    def __write_files(self):
        """Write all files for the blog to _site

        Convert all templates to straight HTML
        Copy other non-template files directly"""
        #find mako templates in template_dir
        for root, dirs, files in os.walk("."):
            if root.startswith("./"):
                root = root[2:]
            for d in list(dirs):
                #Exclude some dirs
                d_path = util.path_join(root,d)
                if util.should_ignore_path(d_path):
                    logger.debug("Ignoring directory: " + d_path)
                    dirs.remove(d)
            try:
                util.mkdir(util.path_join(self.output_dir, root))
            except OSError: #pragma: no cover
                pass
            for t_fn in files:
                t_fn_path = util.path_join(root, t_fn)
                if util.should_ignore_path(t_fn_path):
                    #Ignore this file.
                    logger.debug("Ignoring file: " + t_fn_path)
                    continue
                elif t_fn.endswith(".mako"):
                    logger.info("Processing mako file: " + t_fn_path)
                    #Process this template file
                    t_name = t_fn[:-5]
                    t_file = open(t_fn_path)
                    template = Template(t_file.read().decode("utf-8"),
                                        output_encoding="utf-8",
                                        lookup=self.template_lookup)
                    #Remember the original path for later when setting context
                    template.bf_meta = {"path":t_fn_path}
                    t_file.close()
                    path = util.path_join(self.output_dir, root, t_name)
                    html_file = open(path, "w")
                    html = self.template_render(template)
                    #Write to disk
                    html_file.write(html)
                else:
                    #Copy this non-template file
                    f_path = util.path_join(root, t_fn)
                    logger.debug("Copying file: " + f_path)
                    out_path = util.path_join(self.output_dir, f_path)
                    if self.config.site.overwrite_warning and os.path.exists(out_path):
                        logger.warn("Location is used more than once: {0}".format(f_path))
                    if self.bf.config.site.use_hard_links:
                        # Try hardlinking first, and if that fails copy
                        try:
                            os.link(f_path, out_path)
                        except StandardError:
                            shutil.copyfile(f_path, out_path)
                    else:
                        shutil.copyfile(f_path, out_path)

    def __init_plugins(self):
        #Run plugin defined init methods
        plugin.init_plugins()
        
    def __init_filters_controllers(self):
        #Run filter/controller defined init methods
        filter.init_filters()
        controller.init_controllers(namespace=self.bf.config.controllers)
        
    def __run_controllers(self):
        """Run all the controllers in the _controllers directory"""
        namespaces = [self.bf.config]
        for plugin in self.bf.config.plugins.values():
            if plugin.enabled:
                namespaces.append(plugin)
        controller.run_all(namespaces)
        
    def template_render(self, template, attrs={}):
        """Render a template"""
        #Create a context object that is fresh for each template render
        self.bf.template_context = cache.Cache(**attrs)
        #Provide the name of the template we are rendering:
        self.bf.template_context.template_name = template.uri
        try:
            #Static pages will have a template.uri like memory:0x1d80a90
            #We conveniently remembered the original path to use instead.
            self.bf.template_context.template_name = template.bf_meta['path']
        except AttributeError:
            pass
        attrs['bf'] = self.bf
        #Provide the template with other user defined namespaces:
        for name, obj in self.bf.config.site.template_vars.items():
            attrs[name] = obj
        try:
            return template.render(**attrs)
        except: #pragma: no cover
            logger.error("Error rendering template")
            print(mako_exceptions.text_error_template().render())
        finally:
            del self.bf.template_context

    def materialize_template(self, template_name, location, attrs={}, lookup=None):
        """Render a named template with attrs to a location in the _site dir"""
        if lookup==None:
            lookup = self.template_lookup
        template = lookup.get_template(template_name)
        template.output_encoding = "utf-8"
        rendered = self.template_render(template, attrs)
        path = util.path_join(self.output_dir, location)
        #Create the path if it doesn't exist:
        util.mkdir(os.path.split(path)[0])
        if self.config.site.overwrite_warning and os.path.exists(path):
            logger.warn("Location is used more than once: {0}".format(location))
        f = open(path, "w")
        f.write(rendered)
        f.close()
