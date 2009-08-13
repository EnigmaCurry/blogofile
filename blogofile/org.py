#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
org.py convert org source file into html file 
"""

__author__ = "Jaemok Jeong(jmjeong@gmail.com)"
__date__   = "Tue Aug 11 12:50:17 2009"


import os
import tempfile
import logging
import re
import sys
import commands
from BeautifulSoup import BeautifulSoup

from main import logger
import config

logging.getLogger("org").setLevel(logging.ERROR)

class EmacsNotFoundException(Exception):
    pass

# emacs = """/Applications/Emacs.app/Contents/MacOS/Emacs --load=/tmp/htmlize.el --batch --visit=%s --funcall org-export-as-html-batch"""

import util

class org:
    """
    Convert org file into html
    """
    def __init__(self, source, config):
        self.source    = source
        return self.__convert()
        
    def __convert(self):
        """
        Convert org file into html file

        It composes org-content with source, preamble, and postample.
        Launches emacs and convert the org-content into html file.

        Generated html file is processed with BeautifulSoup module to
        extract body section and title and categories.

        self.content  = body
        self.title    = title (which is first '*' in org-file)
        self.category = categories (which is tags in first '*' in org-file)
        self.date     = date (which is scheduled file?)
        """
        tempFile = tempfile.NamedTemporaryFile(suffix='.org')
        try:
            tempFile.write(config.orgmode_preamble)
            tempFile.write("\n")
        except AttributeError:
            pass
        tempFile.write(self.source)
        tempFile.flush()

        pname = ""

        try:
            pname = config.emacs_binary
        except AttributeError:
            raise EmacsNotFoundException, "Emacs binary is not defined"

        try:
            pname += " --load=%s" % config.emacs_preload_elisp
        except AttributeError:
            pass

        pname += " --funcall org-export-as-html-batch --visit=%s"
        pname = pname % tempFile.name
        logger.info(pname)

        status, output = commands.getstatusoutput(pname)
        logger.debug("Orgfile convering output ===\n %s"%output)
        if status:
            raise EmacsNotFoundException, "orgfile converting failed"
        
        html = tempFile.name[:-4] + '.html'
        tempFile.close()

        content = open(html, 'r').read()

        # remote the temporary file
        os.remove(html)
            
        soup = BeautifulSoup(content.decode('utf-8'))
        self.title = re.sub('&nbsp;', '', soup.h2.contents[0]).strip()

        if soup.h2.span != None:
            self.categories = set(soup.h2.span.string.split('&nbsp;'))
        else:
            self.categories = None
        
        soup.body.div.h2.extract()  # delete h2 section (title and category)
        self.content = soup.body.div.prettify()
        
if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
    
