import os
import pkgutil
import zipfile
import StringIO
import logging
import shutil
import imp
import traceback
from .. import __version__ as bf_version

logger = logging.getLogger("blogofile.site_init")
    
from .. import util

available_sites = [
    # (name of site, description, module)
    ("bare", "A blank site with no blog", "bare"),
    ("simple_blog", "A (very) simple blog with no theme", "simple_blog"),
    ("blogofile.com", "The blogofile.com blog fully themed (requires git)", "blogofile_com.py")
    ]

#These are hidden site templates that are not shown in the list shown in help
hidden_sites = [
    ("blog_unit_test", "A simple site, for unit testing", "blog_unit_test")
    ]

extra_features = {
    "simple_blog": ["blog_filters"],
    "simple_html5_blog": ["blog_features", "html5_blog_features"],
    "blog_unit_test":["blog_features"],
    "blog_features":["blog_controller","blog_templates","blog_filters",
                     (util.rewrite_strings_in_files,
                     {"existing_string":"@BLOGOFILE_VERSION_REPLACED_HERE@",
                      "replacement_string":bf_version,
                      "paths":["_controllers/blog/__init__.py"]})]
    }

all_sites = list(available_sites)
all_sites.extend(hidden_sites)

site_modules = dict((x[0], x[2]) for x in all_sites)

def zip_site_init(): #pragma: no cover .. only used by setuptools
    """Zip up all of the subdirectories of site_init

    This function should only be called by setuptools
    """
    try: 
        curdir = os.getcwd()
        root = os.path.join(curdir, "blogofile", "site_init")
        for d in os.listdir(root):
            d = os.path.join(root, d)
            if os.path.isdir(d):
                os.chdir(root)
                zf = d + ".zip"
                z = zipfile.ZipFile(zf, "w")
                os.chdir(d)
                for dirpath, dirnames, filenames in os.walk(os.curdir):
                    if len(filenames) == 0:
                        #This is an empty directory, add it anyway:
                        z.writestr(zipfile.ZipInfo(dirpath+"/"), '')
                    for fn in filenames:
                        z.write(os.path.join(dirpath, fn))
                z.close()
    finally:
        os.chdir(curdir)

def do_help(): #pragma: no cover
    print("Available site templates:\n")
    for meta in available_sites:
        site, description = meta[:2]
        print("   {0}- {1}".format(site.ljust(20), description))
    print("")
    print("For example, create a simple site, with a blog, and no theme:\n")
    print("   blogofile init simple_blog\n")

def import_site_init(feature):
    """Copy a site_init template to the build dir.

    site_init templates can be of four forms:
      1) A directory
      2) A zip file
      3) A .py file
      4) A function and args tuple
    Directories are usually used in development,
    whereas zip files are used in production.
    .py files and functions are special in that they control how to initialize a site,
    for example, pulling from a git repository."""
    #If the directory exists, just use that.
    if type(feature) == tuple:
        feature[0](**feature[1])
        return
    path = os.path.join(os.path.split(__file__)[0], feature)
    if os.path.isdir(path):
        logger.info(u"Initializing site from directory: " + path)
        for root, dirs, files in os.walk(path):
            for fn in files:
                fn = os.path.join(root, fn)
                dst_fn = fn.replace(path + os.path.sep,"")
                dst_dir = os.path.split(dst_fn)[0]
                util.mkdir(dst_dir)
                shutil.copyfile(fn, dst_fn)
    #If a .py file exists, run with that:
    elif os.path.isfile(path) and path.endswith(".py"):
        mod = imp.load_source("mod", path)
        mod.do_init()
    #Otherwise, load it from the zip file
    else:
        try:
            zip_data = pkgutil.get_data("blogofile.site_init", feature + ".zip")
        except IOError:
            pass
        else:
            logger.info("Initializing feature from zip file: {0}".format(feature))
            zip_file = zipfile.ZipFile(StringIO.StringIO(zip_data))
            for name in zip_file.namelist():
                if name.endswith('/'):
                    util.mkdir(name)
                else:
                    util.mkdir(os.path.split(name)[0])
                    f = open(name, 'wb')
                    f.write(zip_file.read(name))
                    f.close()
    #Recursively import child features of this feature
    try:
        child_features = extra_features[feature]
    except KeyError:
        pass
    else:
        for child_feature in child_features:
            import_site_init(child_feature)

def do_init(args):
    if not args.SITE_TEMPLATE: #pragma: no cover
        do_help()
    else:
        if args.SITE_TEMPLATE not in [x[0] for x in all_sites]: #pragma: no cover
            do_help()
            return
        if len(os.listdir(args.src_dir)) > 0 : #pragma: no cover
            print("This directory is not empty, will not attempt to " \
                    "initialize here : {0}".format(args.src_dir))
            return
        
        print("Initializing the {0} site template...".format(
                args.SITE_TEMPLATE))
        template = site_modules[args.SITE_TEMPLATE]
        import_site_init(template)
