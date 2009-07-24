import re

import pygments
import pygments.formatters
import pygments.lexers
import pygments.util

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }
    
def html_escape(text):
    """Produce entities within text."""
    L=[]
    for c in text:
        L.append(html_escape_table.get(c,c))
    return "".join(L)

def pre_tag_parser(text, occurance):
    """BeautifulSoup, ElementTree, minidom, they all mess with the insides of
    <pre> tags and it's pissing me off. I guess I'll write my own, hope it's not
    terribly buggy.

    returns a tuple representing Xth (occurance) pre tag found in text:
    ( pre_tag_contents,
       tag_attrs,
       start_offset,
       end_offset )"""
    current_start_offset = 0
    attr_re = re.compile(r"""([^ ]+)=(?:(?:"([^"]+)")|(?:'([^"]+)')|([^ >]+))""")
    current_occurance = 0
    while True:
        start_offset = text.find("<pre",current_start_offset)
        end_of_start = text.find(">",start_offset)+1
        end_offset = text.find("</pre",start_offset)
        end_of_end = text.find(">",end_offset)
        if(start_offset==-1 or end_of_start==-1 or end_offset==-1 or end_of_end==-1):
            return None
        current_occurance += 1
        if current_occurance < occurance:
            current_start_offset = end_of_end
            continue
        contents = text[end_of_start:end_offset]
        attrs = {}
        for match in attr_re.findall(text[start_offset:end_of_start]):
            if match[1] != "":
                attrs[match[0]] = match[1]
            elif match[2] != "":
                attrs[match[0]] = match[2]
            elif match[3] != "":
                attrs[match[0]] = match[3]
        return (contents,attrs,start_offset,end_of_end)

def do_syntax_highlight(content,config):
    pre_tag_num = 0
    while True:
        pre_tag_num+=1
        pre_tag_info = pre_tag_parser(content,pre_tag_num)
        if pre_tag_info:
            pre_contents,attrs,start,end = pre_tag_info
            print pre_contents
            try:
                lexer = pygments.lexers.get_lexer_by_name(attrs['lang'])
            except KeyError, pygments.util.ClassNotFound:
                continue
            h_pre = pygments.highlight(
                pre_contents, lexer,
                config.html_formatter)
            #replace in content:
            content=content[:start]+h_pre+content[end+1:]
        else:
            break
    return content
    
