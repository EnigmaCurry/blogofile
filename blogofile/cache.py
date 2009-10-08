import sys

class Cache(dict):
    """A dummy object used for attatching things we want to remember"""
    def __init__(self,**kw):
        dict.__init__(self,kw)
        self.__dict__ = self

#The main blogofile cache object, transfers state between templates
bf = Cache()
sys.modules['blogofile_bf'] = bf
