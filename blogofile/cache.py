# -*- coding: utf-8 -*-
import sys
from . import __version__ as bf_version


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
    def __init__(self, **kw):
        dict.__init__(self, kw)
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
    >>> c.sub.d['one'].value.stuff = "whatever"
    >>> c.sub.d.one.value.stuff
    'whatever'
    >>> c.sub.d['one'].value.stuff
    'whatever'
    >>> c.sub.d['one.value.stuff']
    'whatever'
    >>> c.sub.d['one.value.stuff'] = "whatever2"
    >>> c.sub.d.one.value.stuff
    'whatever2'
    >>> list(c.sub.d.one.value.items())
    [('stuff', 'whatever2')]
    >>> "doesn't have this" in c.sub.d
    False
    """
    def __getattr__(self, attr):
        if not attr.startswith("_") and \
                "(" not in attr and \
                "[" not in attr and \
                attr != "trait_names":
            c = HierarchicalCache()
            Cache.__setitem__(self, attr, c)
            return c
        else:
            raise AttributeError

    def __getitem__(self, item):
        if(type(item) == slice or not hasattr(item, "split")):
            raise TypeError("HierarchicalCache objects are not indexable nor "
                            "sliceable. If you were expecting another object "
                            "here, a parent cache object may be inproperly "
                            "configured.")
        dotted_parts = item.split(".")
        try:
            c = self.__getattribute__(dotted_parts[0])
        except AttributeError:
            c = self.__getattr__(item)
        for dotted_part in dotted_parts[1:]:
            c = getattr(c, dotted_part)
        return c

    def __call__(self):
        raise TypeError("HierarchicalCache objects are not callable. If "
                        "you were expecting this to be a method, a "
                        "parent cache object may be inproperly configured.")

    def __setitem__(self, key, item):
        c = self
        try:
            try:
                dotted_parts = key.split(".")
            except AttributeError:
                return
            if len(dotted_parts) > 1:
                c = self.__getitem__(".".join(dotted_parts[:-1]))
                key = dotted_parts[-1]
        finally:
            Cache.__setitem__(c, key, item)

#The main blogofile cache object, transfers state between templates
bf = HierarchicalCache()


def setup_bf():
    global bf
    sys.modules['blogofile_bf'] = bf
    bf.__version__ = bf_version
    bf.cache = sys.modules['blogofile.cache']


def reset_bf(assign_modules=True):
    global bf
    bf.clear()
    setup_bf()

    if assign_modules:
        from . import config, util, server, filter, controller, template
        bf.config = config
        bf.util = util
        bf.server = server
        bf.filter = filter
        bf.controller = controller
        bf.template = template
    return bf

setup_bf()
