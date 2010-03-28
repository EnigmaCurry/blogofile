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
import urlparse
import re
import operator
import imp

from mako.template import Template
from mako.lookup import TemplateLookup
from mako import exceptions as mako_exceptions
import BeautifulSoup

import util
import config
import cache
import post
import filter

logger = logging.getLogger("blogofile.writer")

class Writer:
    def __init__(self, output_dir):
        self.config = config
        #Base templates are templates (usually in ./_templates) that are only
        #referenced by other templates.
        self.base_template_dir = util.path_join(".","_templates")
        self.output_dir        = output_dir
        self.template_lookup = TemplateLookup(
            directories=[".", self.base_template_dir],
            input_encoding='utf-8', output_encoding='utf-8',
            encoding_errors='replace')

    def __load_bf_cache(self):
        #Template cache object, used to transfer state to/from each template:
        self.bf = cache.bf
        self.bf.config = self.config
        self.bf.writer = self
        self.bf.util = util
        self.bf.logger = logger
        self.bf.filter = filter
        if self.config.blog_enabled == True:
            self.bf.posts = post.parse_posts("_posts")
            self.bf.blog_dir = util.path_join(self.output_dir,self.config.blog_path)
            
    def write_site(self):
        self.__setup_output_dir()
        self.__load_bf_cache()
        self.__run_controllers()
        self.__write_files()
            
    def __setup_output_dir(self):
        """Setup the staging directory"""
        import sys
        if os.path.isdir(self.output_dir): #pragma: no cover
            # I *would* just shutil.rmtree the whole thing and recreate it,
            # but I want the output_dir to retain it's same inode on the
            # filesystem to be compatible with some HTTP servers.
            # So this just deletes the *contents* of output_dir
            for f in os.listdir(self.output_dir):
                f = util.path_join(self.output_dir,f)
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
            excluded_roots = []
            if root.startswith("./"):
                root = root[2:]
            for d in list(dirs):
                #Exclude some dirs
                d_path = util.path_join(root,d)
                if util.should_ignore_path(d_path):
                    logger.debug("Ignoring directory: "+d_path)
                    dirs.remove(d)
            try:
                util.mkdir(util.path_join(self.output_dir, root))
            except OSError: #pragma: no cover
                pass
            for t_fn in files:
                t_fn_path = util.path_join(root,t_fn)
                if util.should_ignore_path(t_fn_path):
                    #Ignore this file.
                    logger.debug("Ignoring file: "+t_fn_path)
                    continue
                elif t_fn.endswith(".mako"):
                    logger.info("Processing mako file: "+t_fn_path)
                    #Process this template file
                    t_name = t_fn[:-5]
                    t_file = open(t_fn_path)
                    template = Template(t_file.read().decode("utf-8"),
                                        output_encoding="utf-8",
                                        lookup=self.template_lookup)
                    t_file.close()
                    path = util.path_join(self.output_dir,root,t_name)
                    html_file = open(path,"w")
                    html = self.template_render(template)
                    #Write to disk
                    html_file.write(html)
                else:
                    #Copy this non-template file
                    f_path = util.path_join(root, t_fn)
                    logger.debug("Copying file: "+f_path)
                    shutil.copyfile(f_path,util.path_join(self.output_dir,f_path))
        
    def __run_controllers(self):
        """Run all the controllers in the _controllers directory"""
        #Store imported controllers on the bf cache
        self.bf.controllers = cache.Cache()
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

    def template_render(self, template, attrs={}):
        """Render a template"""
        #Create a context object that is fresh for each template render
        self.bf.context = cache.Cache(**attrs)
        #Provide the name of the template we are rendering:
        self.bf.context.template_name = template.uri
        attrs['bf'] = self.bf
        try:
            return template.render(**attrs)
        except: #pragma: no cover
            logger.error("Error rendering template")
            print(mako_exceptions.text_error_template().render())
        del self.bf.context

    def materialize_template(self, template_name, location, attrs={}):
        """Render a named template with attrs to a location in the _site dir"""
        template = self.template_lookup.get_template(template_name)
        template.output_encoding = "utf-8"
        rendered = self.template_render(template, attrs)
        path = util.path_join(self.output_dir,location)
        #Create the path if it doesn't exist:
        util.mkdir(os.path.split(path)[0])
        f = open(path,"w")
        f.write(rendered)
        f.close()
