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

logger = logging.getLogger("blogofile.writer")

class Writer:
    def __init__(self, output_dir):
        self.config = config
        #Base templates are templates (usually in ./_templates) that are only
        #referenced by other templates.
        self.base_template_dir = os.path.join(".","_templates")
        self.output_dir        = output_dir
        self.template_lookup = TemplateLookup(
            directories=[".", self.base_template_dir],
            input_encoding='utf-8', output_encoding='utf-8',
            encoding_errors='replace')
        
    def write_site(self):
        self.__setup_output_dir()
        self.__write_files()
        self.__run_auto_templates()
            
    def __setup_output_dir(self):
        # Clear out the old staging directory.  I *would* just shutil.rmtree
        # the whole thing and recreate it, but I want the output_dir to
        # retain it's same inode on the filesystem to be compatible with some
        # HTTP servers. So this just deletes the *contents* of output_dir
        try:
            util.mkdir(self.output_dir)
        except OSError:
            pass
        for f in os.listdir(self.output_dir):
            f = os.path.join(self.output_dir,f)
            try:
                os.remove(f)
            except OSError:
                pass
            try:
                shutil.rmtree(f)
            except OSError:
                pass
            
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
                d_path = os.path.join(root,d)
                if util.should_ignore_path(d_path):
                    logger.info("Ignoring directory : "+d_path)
                    dirs.remove(d)
            try:
                util.mkdir(os.path.join(self.output_dir, root))
            except OSError:
                pass
            for t_fn in files:
                t_fn_path = os.path.join(root,t_fn)
                if util.should_ignore_path(t_fn_path):
                    #Ignore this file.
                    logger.info("Ignoring file : "+t_fn_path)
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
                    path = os.path.join(self.output_dir,root,t_name)
                    html_file = open(path,"w")
                    html = self.template_render(template)
                    #Write to disk
                    html_file.write(html)
                else:
                    #Copy this non-template file
                    f_path = os.path.join(root, t_fn)
                    logger.info("Copying file : "+f_path)
                    shutil.copyfile(f_path,os.path.join(self.output_dir,f_path))
        
    def __run_auto_templates(self):
        """Renders all the templates in _templates/ that have associated .py
        files"""
        for py_file in [p for p in os.listdir("_templates") if
                        p.endswith(".py")]:
            mod = imp.load_source("auto_template_mod",os.path.join("_templates",py_file))
            for k,v in self.config.cache.__dict__.items():
                mod.__dict__[k] = v
            mod.bf = cache.Cache()
            mod.bf.config = self.config
            mod.bf.writer = self
            mod.bf.util = util
            mod.bf.logger = logger
            logger.info("Running automatic template: "+py_file)
            mod.run()
            
    def template_render(self, template, attrs={}):
        for k,v in self.__dict__.items():
            attrs[k] = v
        for k,v in config.cache.__dict__.items():
            attrs[k] = v
        try:
            return template.render(**attrs)
        except:
            logger.error("Error rendering template")
            print(mako_exceptions.text_error_template().render())
    
