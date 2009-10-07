import logging
import imp

import util

logger = logging.getLogger("blogofile.filter")

def run_chain(chain, content):
    """Run content through a filter chain"""
    for fn in chain.split(","):
        f = load_filter(fn.strip(" "))
        logging.debug("Applying filter: "+fn)
        content = f.run(content)
    logging.debug("Content:"+content)
    return content

def load_filter(name):
    """Load a filter directory from the site's _filters directory"""
    logger.debug("Loading filter: "+name)
    try:
        return imp.load_source("filter_"+name,util.path_join("_filters",name+".py"))
    except:
        logging.error("Cannot load filter: "+name)
        raise
