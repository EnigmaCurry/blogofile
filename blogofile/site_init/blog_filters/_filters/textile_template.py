import textile

config = {
    'name': "Textile",
    'description': "Renders textile formatted text to HTML",
    'aliases': ['textile']
    }


def run(content):
    return textile.textile(content)
