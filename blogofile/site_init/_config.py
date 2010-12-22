# -*- coding: utf-8 -*-

######################################################################
# This is the main Blogofile configuration file.
# www.Blogofile.com
#
# This is the canonical _config.py with every single default setting
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

#### Blog Settings ####
blog = controllers.blog

## blog_enabled -- Should the blog be enabled?
#  (You don't _have_ to use blogofile to build blogs)
blog.enabled = False

## blog_path -- Blog path.
#  This is the path of the blog relative to the site_url.
#  If your site_url is "http://www.yoursite.com/~ryan"
#  and you set blog_path to "/blog" your full blog URL would be
#  "http://www.yoursite.com/~ryan/blog"
#  Leave blank "" to set to the root of site_url
blog.path = "/blog"

## blog_name -- Your Blog's name.
# This is used repeatedly in default blog templates
blog.name = "Your Blog's Name"

## blog_description -- A short one line description of the blog
# used in the RSS/Atom feeds.
blog.description = "Your Blog's short description"

## blog_timezone -- the timezone that you normally write your blog posts from
blog.timezone = "US/Eastern"

## blog_posts_per_page -- Blog posts per page
blog.posts_per_page = 5

# Automatic Permalink
# (If permalink is not defined in post article, it's generated
#  automatically based on the following format:)
# Available string replacements:
# :year, :month, :day -> post's date
# :title              -> post's title
# :uuid               -> sha hash based on title
# :filename           -> article's filename without suffix
blog.auto_permalink.enabled = True
# This is relative to site_url
blog.auto_permalink.path = ":blog_path/:year/:month/:day/:title"

######################################################################
# Intermediate Settings
######################################################################
#### Disqus.com comment integration ####
blog.disqus.enabled = False
blog.disqus.name = "your_disqus_name"

#### Emacs Integration ####
blog.emacs_orgmode_enabled = False
# emacs binary (orgmode must be installed)
blog.emacs_binary = "/usr/bin/emacs"               # emacs 22 or 23 is recommended
blog.emacs_preload_elisp = "_emacs/setup.el"          # preloaded elisp file
blog.emacs_orgmode_preamble = r"#+OPTIONS: H:3 num:nil toc:nil \n:nil"   # added in preamble

#### Blog post syntax highlighting ####
# You can change the style to any builtin Pygments style
# or, make your own: http://pygments.org/docs/styles
filters.syntax_highlight.style = "murphy"
filters.syntax_highlight.css_dir = "/css"

#### Custom blog index ####
# If you want to create your own index page at your blog root
# turn this on. Otherwise blogofile assumes you want the
# first X posts displayed instead
blog.custom_index = False

#### Post excerpts ####
# If you want to generate excerpts of your posts in addition to the
# full post content turn this feature on
blog.post_excerpts.enabled = True
blog.post_excerpts.word_length = 25
#Also, if you don't like the way the post excerpt is generated
#You can define assign a new function to blog.post_excerpts.method
#This method must accept the following arguments: (content, num_words)

#### Blog pagination directory ####
# blogofile places extra pages of your blog in
# a secondary directory like the following:
# http://www.yourblog.com/blog_root/page/4
# You can rename the "page" part here:
blog.pagination_dir = "page"

#### Blog category directory ####
# blogofile places extra pages of your or categories in
# a secondary directory like the following:
# http://www.yourblog.com/blog_root/category/your-topic/4
# You can rename the "category" part here:
blog.category_dir = "category"

#### Post encoding ####
blog.post_encoding = "utf-8"

######################################################################
# Advanced Settings
######################################################################
# These are the default ignore patterns for excluding files and dirs
# from the _site directory
# These can be strings or compiled patterns.
# Strings are assumed to be case insensitive.
site.file_ignore_patterns = [
    r".*/_.*",      # All files that start with an underscore
    r".*/#.*",      # Emacs temporary files
    r".*~$",        # Emacs temporary files
    r".*/\..*\.swp", # Vim swap files
    r".*/\.git$",   # Git VCS dir
    r".*/.gitignore", # Git ignored files
    r".*/\.hg$",    # Mercurial VCS dir
    r".*/.hgignore", # Mercurial ignored files
    r".*/\.bzr$",   # Bazaar VCS dir
    r".*/\.svn$",   # Subversion VCS dir
    r".*/CVS$",     # CVS dir
    ]

#### Default post filters ####
# If a post does not specify a filter chain, use the 
# following defaults based on the post file extension:
blog.post_default_filters = {
    "markdown": "syntax_highlight, markdown",
    "textile": "syntax_highlight, textile",
    "org": "syntax_highlight, org",
    "rst": "syntax_highlight, rst",
    "html": "syntax_highlight"
}

### Pre/Post build hooks:
def pre_build():
    #Do whatever you want before the _site is built
    pass

def post_build():
    #Do whatever you want after the _site is built
    pass
