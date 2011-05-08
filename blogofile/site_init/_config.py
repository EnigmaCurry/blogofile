######################################################################
# This is the main Blogofile configuration file.
# www.Blogofile.com
#
# This is the canonical _config.py with every single default setting.
#
# Don't edit this file directly; create your own _config.py (from
# scratch or using 'blogofile init') and your settings will override
# these defaults.
#
######################################################################

######################################################################
# Basic Settings
#  (almost all sites will want to configure these settings)
######################################################################
## site.url -- Your site's full URL
# Your "site" is the same thing as your _site directory.
#  If you're hosting a blogofile powered site as a subdirectory of a larger
#  non-blogofile site, then you would set the site_url to the full URL
#  including that subdirectory: "http://www.yoursite.com/path/to/blogofile-dir"
site.url = "http://www.example.com"

## site.author -- Your name, the author of the website.
# This is optional. If set to anything other than None, the
# simple_blog template creates a meta tag for the site author.
site.author = None

######################################################################
# Advanced Settings
######################################################################
# Use hard links when copying files. This saves disk space and shortens
# the time to build sites that copy lots of static files.
# This is turned off by default though, because hard links are not
# necessarily what every user wants.
site.use_hard_links = False
#Warn when we're overwriting a file?
site.overwrite_warning = True
# These are the default ignore patterns for excluding files and dirs
# from the _site directory
# These can be strings or compiled patterns.
# Strings are assumed to be case insensitive.
site.file_ignore_patterns = [
    # All files that start with an underscore
    ".*/_.*",
    # Emacs autosave files
    ".*/#.*",
    # Emacs/Vim backup files
    ".*~$",
    # Vim swap files
    ".*/\..*\.swp$",
    # VCS directories
    ".*/\.(git|hg|svn|bzr)$",
    # Git and Mercurial ignored files definitions
    ".*/.(git|hg)ignore$",
    # CVS dir
    ".*/CVS$",
    ]

from blogofile.template import MakoTemplate, JinjaTemplate, \
    MarkdownTemplate, RestructuredTextTemplate, TextileTemplate
#The site base template filename:
site.base_template = "site.mako"
#Template engines mapped to file extensions:
templates.engines = HC(
    mako = MakoTemplate,
    jinja = JinjaTemplate,
    jinja2 = JinjaTemplate,
    markdown = MarkdownTemplate,
    rst = RestructuredTextTemplate,
    textile = TextileTemplate
    )

#Template content blocks:
templates.content_blocks = HC(
    mako = HC(
        pattern = re.compile("\${\W*next.body\(\)\W*}"),
        replacement = "${next.body()}"
        ),
    jinja2 = HC(
        pattern = re.compile("{%\W*block content\W*%}.*?{%\W*endblock\W*%}", re.MULTILINE|re.DOTALL),
        replacement = "{% block content %} {% endblock %}"
        ),
    filter = HC(
        pattern = re.compile("_^"), #Regex that matches nothing
        replacement = "~~!`FILTER_CONTENT_HERE`!~~",
        default_chains = HC(
            markdown = "syntax_highlight, markdown",
            rst = "syntax_highlight, rst"
            )
        )
    )

### Pre/Post build hooks:
def pre_build():
    #Do whatever you want before the _site is built.
    pass

def post_build():
    #Do whatever you want after the _site is built successfully.
    pass

def build_exception():
    #Do whatever you want if there is an unrecoverable error in building the site.
    pass

def build_finally():
    #Do whatever you want after the _site is built successfully OR after a fatal error
    pass
