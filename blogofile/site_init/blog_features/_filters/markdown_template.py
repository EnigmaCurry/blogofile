import markdown
import logging
from blogofile.cache import HierarchicalCache as HC

config = {
    "name": "Markdown",
    "description": "Renders markdown formatted text to HTML",
    "aliases": ["markdown"],
    "extensions_enabled": {"def_list"    : True,
                           "abbr"        : True,
                           "footnotes"   : True,
                           "fenced_code" : True,
                           "headerid"    : True,
                           "tables"      : True},
    "extension_parameters": {"headerid": {"level":1,"forceid":True}}
    }

#Markdown logging is noisy, pot it down:
logging.getLogger("MARKDOWN").setLevel(logging.ERROR)

extensions = []

def init():
    #Create the list of enabled extensions with their arguments
    for ext, enabled in config["extensions_enabled"].items():
        if enabled:
            params = []
            try:
                p = config["extension_parameters"][ext]
            except KeyError:
                extensions.append(ext)
                continue
            for param,value in p.items():
                params.append(param+"="+repr(value))
            extensions.append(ext+"("+",".join(params)+")")
    print extensions
    
def run(content):
    return markdown.markdown(content, extensions)
