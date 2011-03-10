# -*- coding: utf-8 -*-

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
## site_url -- Your site's full URL
# Your "site" is the same thing as your _site directory.
#  If you're hosting a blogofile powered site as a subdirectory of a larger
#  non-blogofile site, then you would set the site_url to the full URL
#  including that subdirectory: "http://www.yoursite.com/path/to/blogofile-dir"
site.url = "http://www.yoursite.com"

######################################################################
# Intermediate Settings
######################################################################
#### Blog post syntax highlighting ####
# You can change the style to any builtin Pygments style
# or, make your own: http://pygments.org/docs/styles
filters.syntax_highlight.style = "murphy"
filters.syntax_highlight.css_dir = "/css"

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
    # Emacs temporary files
    ".*/#.*",
    # Emacs/Vim temporary files
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

### Pre/Post build hooks:
def pre_build():
    #Do whatever you want before the _site is built
    pass

def post_build():
    #Do whatever you want after the _site is built successfully.
    pass

def build_finally():
    #Do whatever you want after the _site is built successfully OR after a fatal error
    pass
