"""
Template abstraction for Blogofile to support multiple engines.

Templates are dictionaries. Any key/value pairs stored are supplied to
the underlying template as name/values.
"""
import sys
import re
import os.path
import logging
import tempfile

import mako
import mako.template
import mako.lookup

import jinja2

from . import util
from .cache import Cache, bf

bf.template = sys.modules['blogofile.template']

base_template_dir = util.path_join(".","_templates")
logger = logging.getLogger("blogofile.writer")
template_content_place_holder = re.compile("~~!`TEMPLATE_CONTENT_HERE`!~~")

class TemplateEngineError(Exception):
    pass

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
    template_lookup = None
    def __init__(self, template_name, lookup=None, src=None):
        Template.__init__(self, template_name)
        self.create_lookup()
        if lookup:
            #Make sure it's a mako environment:
            if type(lookup) != mako.lookup.TemplateLookup:
                raise TemplateEngineError(
                    "MakoTemplate was passed a non-mako lookup environment:"
                    " {0}".format(lookup))
            self.template_lookup = lookup
        self.add_template_path(bf.writer.temp_proc_dir)
        #Templates can be provided three ways:
        # 1) src is a template passed via string
        # 2) template_name can be a path to a file
        # 3) template_name can be a name to lookup
        if src:
            self.mako_template = mako.template.Template(
                src,
                output_encoding="utf-8",
                lookup=self.template_lookup)
        elif os.path.isfile(template_name):
            with open(self.template_name) as t_file:
                self.mako_template = mako.template.Template(
                    t_file.read(),
                    output_encoding="utf-8",
                    lookup=self.template_lookup)
        else:
            self.mako_template = self.template_lookup.get_template(template_name)
            self.mako_template.output_encoding = "utf-8"
    @classmethod
    def create_lookup(cls):
        if MakoTemplate.template_lookup is None:
            MakoTemplate.template_lookup = mako.lookup.TemplateLookup(
                directories=[".", base_template_dir],
                input_encoding='utf-8', output_encoding='utf-8',
                encoding_errors='replace')
    def add_template_path(self, path, lookup=None):
        if lookup:
            pass
        elif self == None:
            MakoTemplate.create_lookup()
            lookup = MakoTemplate.template_lookup
        else:
            lookup = self.template_lookup
        if path not in lookup.directories:
            lookup.directories.append(path)
    def render(self, path=None):
        self.render_prep()
        #Make sure bf_base_template is defined
        if "bf_base_template" in self:
            bf_base_template = os.path.split(self["bf_base_template"])[1]
            self.template_lookup.put_template(
                "bf_base_template", self.template_lookup.get_template(
                    bf_base_template))
        else:
            self.template_lookup.put_template(
                "bf_base_template",
                self.template_lookup.get_template(bf.config.site.base_template))
        try:
            rendered = self.mako_template.render(**self)
            if path:
                self.write(path, rendered)
            return rendered
        except:
            logger.error("Error rendering template: {0}".format(
                    self.template_name))
            print((mako.exceptions.text_error_template().render()))
            raise
        finally:
            self.render_cleanup()

class JinjaTemplateLoader(jinja2.FileSystemLoader):
    def __init__(self, searchpath):
        jinja2.FileSystemLoader.__init__(self, searchpath)
        self.bf_base_template = bf.util.path_join("_templates",bf.config.site.base_template)
    def get_source(self, environment, template):
        if template == "bf_base_template":
            with open(self.bf_base_template) as f:
                return (f.read(), self.bf_base_template, lambda: False)
        else:
            return super(jinja2.FileSystemLoader,self).\
                get_source(environment, template)
            
class JinjaTemplate(Template):
    name = "jinja2"
    template_lookup = None
    def __init__(self, template_name, lookup=None, src=None):
        Template.__init__(self, template_name)
        self.create_lookup()
        if lookup:
            #Make sure it's a jinja2 environment:
            if type(lookup) != jinja2.Environment:
                raise TemplateEngineError(
                    "JinjaTemplate was passed a non-jinja lookup environment:"
                    " {0}".format(lookup))
            self.template_lookup = lookup
        self.add_template_path(bf.writer.temp_proc_dir)
        #Templates can be provided three ways:
        # 1) src is a template passed via string
        # 2) template_name can be a path to a file
        # 3) template_name can be a name to lookup
        
        # Jinja needs to save the loading of the source until render
        # time in order to get the attrs into the loader.
        # Just save the params for later use:
        self.src = src
    @classmethod
    def create_lookup(cls):
        if cls.template_lookup is None:
            cls.template_lookup = jinja2.Environment(
                loader=JinjaTemplateLoader([base_template_dir,
                                            bf.writer.temp_proc_dir]))
    def add_template_path(self, path, lookup=None):
        if lookup:
            pass
        if self == None:
            JinjaTemplate.create_lookup()
            lookup = JinjaTemplate.template_lookup
        else:
            lookup = self.template_lookup
        if path not in lookup.loader.searchpath:
            lookup.loader.searchpath.append(path)
    def render(self, path=None):
        #ensure that bf_base_template is set:
        if "bf_base_template" in self:
            self.template_lookup.loader.bf_base_template = self["bf_base_template"]
        else:
            self["bf_base_template"] = self.template_lookup.loader.bf_base_template
        if self.src:
            self.jinja_template = self.template_lookup.from_string(self.src)
        elif os.path.isfile(self.template_name):
            with open(self.template_name) as t_file:
                self.jinja_template = self.template_lookup.from_string(t_file.read())
        else:
            self.jinja_template = self.template_lookup.get_template(self.template_name)
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

def get_engine_for_template_name(template_name):
    #Find which template type it is:
    for extension, engine in bf.config.templates.engines.items():
        if template_name.endswith("."+extension):
            return engine
    else:
        raise TemplateEngineError(
            "Template has no engine defined in bf.config."
            "templates.engines: {0}".format(template_name))

def get_base_template_path():
    return bf.util.path_join("_templates",bf.config.site.base_template)

def get_base_template_src():
    with open(get_base_template_path()) as f:
        return f.read()
    
def materialize_alternate_base_engine(template_name, location, attrs={},
                                      lookup=None, base_engine=None):
    # We can materialize a templates within a foreign template engine
    # with the following procedure:
    
    # 1) Load the base template source, and mark the content block
    # for later replacement.
    #
    # 2) Materialize the jinja template in a temporary location with
    # attrs.
    #
    # 3) Convert the HTML to Mako with ${next.body()} where the old
    # content block was.
    #
    # 4) Materialize the blog template setting blog_base_template to
    # the new template
    if not base_engine:
        base_engine = get_engine_for_template_name(bf.config.site.base_template)
    template_engine = get_engine_for_template_name(template_name)
    base_template_src = get_base_template_src()
    if not lookup:
        lookup = base_engine.template_lookup
    else:
        base_engine.add_template_path(None, bf.writer.temp_proc_dir,lookup)
    #Replace the content block with our own marker:
    prev_content_block = bf.config.templates.content_blocks[base_engine.name]
    new_content_block =  bf.config.templates.content_blocks[template_engine.name]
    base_template_src = prev_content_block.pattern.sub(
        template_content_place_holder.pattern,base_template_src)
    html = str(base_engine(None, src=base_template_src).render(),"utf-8")
    html = template_content_place_holder.sub(new_content_block.replacement,html)
    new_base_template = tempfile.mktemp(suffix="."+template_engine.name,
                                prefix="bf_template",
                                dir=bf.writer.temp_proc_dir)
    new_base_template_name = os.path.split(new_base_template)[1]
    with open(new_base_template,"w") as f:
        f.write(html)
    attrs["bf_base_template"] = new_base_template
    materialize_template(template_name,location,attrs,base_engine=template_engine)
    os.remove(new_base_template)
    
def materialize_template(template_name, location, attrs={}, lookup=None, base_engine=None):
    """Render a named template with attrs to a location in the _site dir"""
    #Find the appropriate template engine based on the file ending:
    template_engine = get_engine_for_template_name(template_name)
    if not base_engine:
        base_engine = get_engine_for_template_name(bf.config.site.base_template)
    #Is the base engine the same as the template engine?
    if base_engine == template_engine or base_engine == template_engine.name:
        template = template_engine(template_name, lookup=lookup)
        template.update(attrs)
        template.render(location)
    else:
        materialize_alternate_base_engine(
            template_name, location, attrs=attrs, lookup=lookup,
            base_engine=base_engine)
