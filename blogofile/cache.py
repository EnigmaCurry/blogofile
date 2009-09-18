class Cache():
    """A caching object for templates and filters

    Templates or filters can create data that they may want another process to
    have access to. This is where they can retrieve it.
    """
