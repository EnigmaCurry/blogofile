---
categories: General Stuff
date: 2009/08/29 15:25:00
title: Syntax highlight test
---
This post contains some highlighted python code:

$$code(lang=python)$
import webbrowser
import hashlib

webbrowser.open("http://xkcd.com/353/")

def geohash(latitude, longitude, datedow):
    """Compute geohash() using the Munroe algorithm.

    >>> geohash(37.421542, -122.085589, b'2005-05-26-10458.68')
    37.857713 -122.544543 """
    
    # http://xkcd.com/426/
    h = hashlib.md5(datedow).hexdigest()
    p, q = [('%f' % float.fromhex('0.' + x)) for x in (h[:16], h[16:32])]
    print('%d%s %d%s' % (latitude, p[1:], longitude, q[1:]))
$$/code

This is accomplished with the built-in [syntax highlighter filter](https://github.com/EnigmaCurry/blogofile/blob/master/blogofile/site_init/blog_features/_filters/syntax_highlight.py)

