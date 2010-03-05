import os

from .. import util

available_sites = [
    # (name of site, description, module)
    ("bare", "A blank site with no blog", "bare"),
    ("simple_blog", "A (very) simple blog with no theme", "simple_blog"),
    ("blogofile.com", "The blogofile.com blog fully themed (requires git)", "blogofile_com")
    ]

#These are hidden site templates that are not shown in the list shown in help
hidden_sites = [
    ("blog_unit_test", "A simple site, for unit testing", "blog_unit_test")
    ]

all_sites = list(available_sites)
all_sites.extend(hidden_sites)

site_modules = dict((x[0],x[2]) for x in all_sites)

def do_help(): #pragma: no cover
    print("Available site templates:\n")
    for meta in available_sites:
        site, description = meta[:2]
        print("   "+site.ljust(20)+"- "+description)
    print("")
    print("For example, create a simple site, with a blog, and no theme:\n")
    print("   blogofile init simple_blog\n")

def do_init(args):
    if not args.SITE_TEMPLATE: #pragma: no cover
        do_help()
    else:
        if args.SITE_TEMPLATE not in [x[0] for x in all_sites]: #pragma: no cover
            do_help()
            return
        if len(os.listdir(args.src_dir)) > 0 : #pragma: no cover
            print("This directory is not empty, will not attempt to initialize here : %s" % args.src_dir)
            return
        
        print("Initializing the %s site template..." % args.SITE_TEMPLATE)
        mod = site_modules[args.SITE_TEMPLATE]
        exec("import "+mod)
        exec(mod+".do_init(args)")

def write_file(path_parts, contents):
    path = os.path.join(*path_parts)
    util.mkdir(os.path.split(path)[0])
    f = open(path,"w")
    f.write(contents)
    f.close()
