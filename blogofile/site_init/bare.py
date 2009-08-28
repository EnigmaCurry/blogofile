def do_init(args):
    #Write an empty config file:
    f=open("_config.py","w")
    f.write("# This is a barren blogofile config file.\n"
            "# See docs at http://www.blogofile.com/documentation"
            "#for config options,\n"
            "#or run 'blogofile help init' to see more complete templates\n"
            "\n"
            "blog_enabled = False")
    f.close()
    f=open("index.html.mako","w")
    f.write("Welcome to <a href='http://www.blogofile.com'>Blogofile</a>.")
    f.close()

