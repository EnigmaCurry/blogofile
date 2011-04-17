"""
Template abstraction for Blogofile to support multiple engines.

Templates are dictionaries. Any key/value pairs stored are supplied to
the underlying template as name/values.
"""
import sys
import os.path
import logging

import mako
import mako.template
import mako.lookup

import jinja2

from . import util
from .cache import Cache, bf

bf.template = sys.modules['blogofile.template']

base_template_dir = util.path_join(".","_templates")
logger = logging.getLogger("blogofile.writer")

class Template(dict):
    name = "base"
    def __init__(self, template_name):
        dict.__init__(self)
        self.template_name = template_name
    def render(self, path=None):
        """Render the template to the specified path on disk, or return a string if None."""
        raise NotImplementedError("Template base class cannot be used directly")
    def write(self, path, rendered):
        path = util.path_join(bf.writer.output_dir, path)
        #Create the parent directories if they don't exist:
        util.mkdir(os.path.split(path)[0])
        if bf.config.site.overwrite_warning and os.path.exists(path):
            logger.warn("Location is used more than once: {0}".format(location))
        with open(path, "bw") as f:
            f.write(rendered)
    def render_prep(self):
        """Gather all the information we want to provide to the template before rendering"""
        for name, obj in list(bf.config.site.template_vars.items()):
            if name not in self:
                self[name] = obj
        #Create a context object that is fresh for each template render:
        bf.template_context = Cache(**self)
        bf.template_context.template_name = self.template_name
        self["bf"] = bf
    def render_cleanup(self):
        """Clean up stuff after we've rendered a template."""
        del bf.template_context
    def __repr__(self):
        return "<{0} file='{1}' {2}>".format(
            self.__class__.__name__, self.template_name, dict.__repr__(self))

class MakoTemplate(Template):
    name = "mako"
    template_lookup = mako.lookup.TemplateLookup(
        directories=[".", base_template_dir],
        input_encoding='utf-8', output_encoding='utf-8',
        encoding_errors='replace')
    def __init__(self, template_name, lookup=None, src=None):
        Template.__init__(self, template_name)
        if not lookup:
            lookup = self.template_lookup
        #Templates can be provided three ways:
        # 1) src is a template passed via string
        # 2) template_name can be a path to a file
        # 3) template_name can be a name to lookup
        if src:
            self.mako_template = mako.template.Template(
                src,
                output_encoding="utf-8",
                lookup=lookup)
        elif os.path.isfile(template_name):
            with open(self.template_name) as t_file:
                self.mako_template = mako.template.Template(
                    t_file.read(),
                    output_encoding="utf-8",
                    lookup=lookup)
        else:
            self.mako_template = lookup.get_template(template_name)
            self.mako_template.output_encoding = "utf-8"
    def render(self, path=None):
        self.render_prep()
        try:
            rendered = self.mako_template.render(**self)
            if path:
                self.write(path, rendered)
            return rendered
        except:
            logger.error("Error rendering template: {0}".format(self.template_name))
            print((mako.exceptions.text_error_template().render()))
            raise
        finally:
            self.render_cleanup()

class JinjaTemplate(Template):
    name = "jinja2"
    template_lookup = jinja2.Environment(loader=jinja2.FileSystemLoader(base_template_dir))
    def __init__(self, template_name, lookup=None, src=None):
        Template.__init__(self, template_name)
        if not lookup:
            lookup = self.template_lookup
        #Templates can be provided three ways:
        # 1) src is a template passed via string
        # 2) template_name can be a path to a file
        # 3) template_name can be a name to lookup
        if src:
            self.jinja_template = lookup.from_string(src)
        elif os.path.isfile(template_name):
            with open(self.template_name) as t_file:
                self.jinja_template = lookup.from_string(t_file.read())
        else:
            self.jinja_template = lookup.get_template(template_name)
    def render(self, path=None):
        self.render_prep()
        try:
            rendered = bytes(self.jinja_template.render(self), "utf-8")
            if path:
                self.write(path, rendered)
            return rendered
        except:
            logger.error("Error rendering template: {0}".format(self.template_name))
            raise
        finally:
            self.render_cleanup()

class TemplateEngineError(Exception):
    pass

def materialize_template(template_name, location, attrs={}, lookup=None):
    """Render a named template with attrs to a location in the _site dir"""
    #Find the appropriate template engine based on the file ending:
    for extension, Engine in bf.config.templates.engines.items():
        if template_name.endswith(extension):
            break
    else:
        raise TemplateEngineError(
            "Template has no engine defined in bf.config."
            "templates.engines: {0}".format(template_name))
    template = Engine(template_name, lookup=lookup)
    template.update(attrs)
    template.render(location)
