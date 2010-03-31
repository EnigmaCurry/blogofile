import sys

class Cache(dict):
    """A cache object used for attatching things we want to remember

    This works like a normal object, attributes that are undefined
    raise an AttributeError
    
    >>> c = Cache()
    >>> c.whatever = "whatever"
    >>> c.whatever
    'whatever'
    >>> c.section.subsection.attribute = "whatever"
    Traceback (most recent call last):
      ...
    AttributeError: 'Cache' object has no attribute 'section'
    """
    def __init__(self,**kw):
        dict.__init__(self,kw)
        self.__dict__ = self

class HierarchicalCache(Cache):
    """A cache object used for attatching things we want to remember
    
    This works differently than a normal object, attributes that
    are undefined do *not* raise an AttributeError but are silently
    created as an additional HierarchicalCache object.
    
    >>> c = HierarchicalCache()
    >>> c.whatever = "whatever"
    >>> c.whatever
    'whatever'
    >>> c.section.subsection.attribute = "whatever"
    >>> c.section.subsection.attribute
    'whatever'
    """
    def __getattr__(self, attr):
        if not attr.startswith("_") and \
                not "(" in attr and \
                not attr == "trait_names": 
            c = HierarchicalCache()
            self.__dict__[attr] = c
            return c

#The main blogofile cache object, transfers state between templates
bf = HierarchicalCache()
sys.modules['blogofile_bf'] = bf
