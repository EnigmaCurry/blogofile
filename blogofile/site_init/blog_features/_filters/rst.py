import docutils.core

def run(content):
    return docutils.core.publish_parts(content, writer_name='html')['html_body']
