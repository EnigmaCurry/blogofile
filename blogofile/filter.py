import logging
import imp

import util

logger = logging.getLogger("blogofile.filter")

__loaded_filters = {} #name -> mod

def run_chain(chain, content):
    """Run content through a filter chain.

    Works with either a string or a sequence of filters"""
    if chain == None: #pragma: no cover
        return content
    if not hasattr(chain,'__iter__'):
        #Not a sequence, must be a string, parse it
        chain = parse_chain(chain)
    for fn in chain:
        f = load_filter(fn)
        logger.debug("Applying filter: "+fn)
        content = f.run(content)
    logger.debug("Content:"+content)
    return util.force_unicode(content)

def parse_chain(chain):
    """Parse a filter chain into a sequence of filters"""
    parts = []
    for p in chain.split(","):
        p = p.strip()
        if p.lower() == "none":
            continue
        if len(p)>0:
            parts.append(p)
    return parts

def load_filter(name):
    """Load a filter directory from the site's _filters directory"""
    logger.debug("Loading filter: "+name)
    try:
        return __loaded_filters[name]
    except KeyError:
        try:
            __loaded_filters[name] = imp.load_source(
                "filter_"+name,util.path_join("_filters",name+".py"))
            return __loaded_filters[name]
        except: #pragma: no cover
            logger.error("Cannot load filter: "+name)
            raise
