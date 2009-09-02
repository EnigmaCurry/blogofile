import os

available_sites = [
    # (name of site, description, module)
    ("bare", "A blank site with no blog", "bare"),
    ("simple_blog", "A (very) simple blog with no theme", "simple_blog"),
    ("blogofile.com", "The blogofile.com blog fully themed (requires git)", "blogofile_com")
    ]
site_modules = dict((x[0],x[2]) for x in available_sites)

def do_help():
    print("Available site templates:\n")
    for meta in available_sites:
        site, description = meta[:2]
        print("   "+site.ljust(20)+"- "+description)
    print("")
    print("For example, create a simple site, with a blog, and no theme:\n")
    print("   blogofile init -t simple_blog\n")

def do_init(args):
    if not args.SITE_TEMPLATE:
        do_help()
    else:
        if args.SITE_TEMPLATE not in [x[0] for x in available_sites]:
            do_help()
            return
        if len(os.listdir(args.config_dir)) > 0 :
            print("This directory is not empty, will not attempt to initialize here : %s" % args.config_dir)
            return
        
        print("Initializing the %s site template..." % args.SITE_TEMPLATE)
        mod = site_modules[args.SITE_TEMPLATE]
        exec("import "+mod)
        exec(mod+".do_init(args)")
