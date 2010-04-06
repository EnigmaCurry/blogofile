import markdown
import logging

#Markdown logging is noisy, pot it down:
logging.getLogger("MARKDOWN").setLevel(logging.ERROR)

def run(content):
    return markdown.markdown(content)
