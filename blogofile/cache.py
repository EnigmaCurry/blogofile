import sys

class Cache(dict):
    """A dummy object used for attatching things we want to remember

    >>> c = Cache()
    >>> c.whatever = "whatever"
    >>> c.whatever
    'whatever'
    >>> c.section.subsection.attribute = "whatever"
    >>> c.section.subsection.attribute
    'whatever'
    """
    def __init__(self,**kw):
        dict.__init__(self,kw)
        self.__dict__ = self
    def __getattr__(self, attr):
        if not attr.startswith("_"):
            c = Cache()
            self.__dict__[attr] = c
            return c

#The main blogofile cache object, transfers state between templates
bf = Cache()
sys.modules['blogofile_bf'] = bf
