# -*- coding: utf-8 -*-
"""Write out the static blog to ./_site based on templates found in
the current working directory.
"""

__author__ = "Ryan McGuire (ryan@enigmacurry.com)"

import logging
import os
import re
import shutil
import tempfile

from . import util
from . import config
from . import cache
from . import filter as _filter
from . import controller
from . import plugin
from . import template


logger = logging.getLogger("blogofile.writer")


class Writer(object):

    def __init__(self, output_dir):
        self.config = config
        # Base templates are templates (usually in ./_templates) that are only
        # referenced by other templates.
        self.base_template_dir = util.path_join(".", "_templates")
        self.output_dir = output_dir

    def __load_bf_cache(self):
        # Template cache object, used to transfer state to/from each template:
        self.bf = cache.bf
        self.bf.writer = self
        self.bf.logger = logger

    def write_site(self):
        self.__load_bf_cache()
        self.__setup_temp_dir()
        try:
            self.__setup_output_dir()
            self.__calculate_template_files()
            self.__init_plugins()
            self.__init_filters_controllers()
            self.__run_controllers()
            self.__write_files()
        finally:
            self.__delete_temp_dir()

    def __setup_temp_dir(self):
        """Create a directory for temporary data.
        """
        self.temp_proc_dir = tempfile.mkdtemp(prefix="blogofile_")
        # Make sure this temp directory is added to each template lookup:
        for engine in self.bf.config.templates.engines.values():
            try:
                engine.add_default_template_path(self.temp_proc_dir)
            except AttributeError:
                pass

    def __delete_temp_dir(self):
        "Cleanup and delete temporary directory"
        shutil.rmtree(self.temp_proc_dir)

    def __setup_output_dir(self):
        """Setup the staging directory"""
        if os.path.isdir(self.output_dir):
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

    def __calculate_template_files(self):
        """Build a regex for template file paths"""
        endings = []
        for ending in self.config.templates.engines.keys():
            endings.append("." + re.escape(ending) + "$")
        p = "(" + "|".join(endings) + ")"
        self.template_file_regex = re.compile(p)

    def __write_files(self):
        """Write all files for the blog to _site.

        Convert all templates to straight HTML.  Copy other
        non-template files directly.
        """
        for root, dirs, files in os.walk("."):
            if root.startswith("./"):
                root = root[2:]
            for d in list(dirs):
                # Exclude some dirs
                d_path = util.path_join(root, d)
                if util.should_ignore_path(d_path):
                    logger.debug("Ignoring directory: " + d_path)
                    dirs.remove(d)
            try:
                util.mkdir(util.path_join(self.output_dir, root))
            except OSError:
                pass
            for t_fn in files:
                t_fn_path = util.path_join(root, t_fn)
                if util.should_ignore_path(t_fn_path):
                    # Ignore this file.
                    logger.debug("Ignoring file: " + t_fn_path)
                    continue
                elif self.template_file_regex.search(t_fn):
                    logger.info("Processing template: " + t_fn_path)
                    # Process this template file
                    html_path = self.template_file_regex.sub("", t_fn)
                    template.materialize_template(
                        t_fn_path,
                        util.path_join(root, html_path))
                else:
                    # Copy this non-template file
                    f_path = util.path_join(root, t_fn)
                    logger.debug("Copying file: " + f_path)
                    out_path = util.path_join(self.output_dir, f_path)
                    if self.config.site.overwrite_warning and \
                            os.path.exists(out_path):
                        logger.warn("Location is used more than once: {0}"
                                    .format(f_path))
                    if self.config.site.use_hard_links:
                        # Try hardlinking first, and if that fails copy
                        try:
                            os.link(f_path, out_path)
                        except Exception:
                            shutil.copyfile(f_path, out_path)
                    else:
                        shutil.copyfile(f_path, out_path)

    def __init_plugins(self):
        # Run plugin defined init methods
        plugin.init_plugins()

    def __init_filters_controllers(self):
        # Run filter/controller defined init methods
        _filter.init_filters()
        controller.init_controllers(namespace=self.bf.config.controllers)

    def __run_controllers(self):
        """Run all the controllers in the _controllers directory.
        """
        namespaces = [self.bf.config]
        for plugin in list(self.bf.config.plugins.values()):
            if plugin.enabled:
                namespaces.append(plugin)
        controller.run_all(namespaces)
