#!/usr/bin/env python
# -*- coding: utf-8 -*-
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Export a Wordpress blog to Blogofile textile format"""

__author__ = "Ryan McGuire (ryan@enigmacurry.com)"
__date__   = "Sun Feb 15 16:55:56 2009"

import os
import sys
import yaml
import wordpress_schema

if __name__ == '__main__':
    #Output textile files in ./_posts
    if os.path.isdir("_posts"):
        print "There's already a _posts directory here, I'm not going to overwrite it."
        sys.exit(1)
    else:
        os.mkdir("_posts")

    for post in wordpress_schema.get_published_posts():
        yaml_data = {
            "title": post.post_title,
            "date": post.post_date.strftime("%Y/%m/%d %H:%M:%S"),
            "permalink": post.permalink(),
            "categories": ", ".join(post.categories()),
            "tags": ", ".join(post.tags()),
            "guid": post.guid
            }
        fn = "%s. %s.html" % (str(post.id).zfill(4), post.post_name.strip())
        print "writing %s" % fn
        f = open(os.path.join("_posts",fn),"w")
        f.write("---\n")
        f.write(yaml.dump(yaml_data, default_flow_style=False))
        f.write("---\n")
        f.write(post.post_content.replace("\r\n","\n"))
        f.close()
