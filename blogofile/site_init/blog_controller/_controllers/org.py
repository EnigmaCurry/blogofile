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
import codecs
import datetime
import pytz
from BeautifulSoup import BeautifulSoup

import blogofile_bf as bf

logger = logging.getLogger("blogofile.org")


class EmacsNotFoundException(Exception):
    pass


post = bf.config.controllers.blog.post.mod


class org(object):
    """
        Class to Convert org file into html file

        It composes org-content with source, preamble, and postample.
        Launches emacs and convert the org-content into html file.

        Generated html file is processed with BeautifulSoup module to
        extract body section and title and categories.

        self.content  = body
        self.title    = title (which is first '*' in org-file)
        self.category = categories (which is tags in first '*' in org-file)
        self.date     = date (which is scheduled file?)

	"""
    def __init__(self, source):
        self.source = source
        return self.__convert()
        
    def __convert(self):
        temp_file = tempfile.NamedTemporaryFile(suffix='.org')
        try:
            temp_file.write(bf.config.blog.emacs_orgmode_preamble)
            temp_file.write("\n")
        except AttributeError:
            pass
        temp_file.write(self.source.encode(bf.config.blog_post_encoding))
        temp_file.flush()

        pname = ""
        try:
            pname = bf.config.blog.emacs_binary
        except AttributeError:
            raise EmacsNotFoundException("Emacs binary is not defined")

        pname += " --batch"
        try:
            if bf.config.blog.emacs_preload_elisp:
                pname += " --load={0}".format(
                        bf.config.blog.emacs_preload_elisp)
        except AttributeError:
            pass

        pname += " --visit={0} --funcall org-export-as-html-batch".format(
                temp_file.name)
        logger.debug("Exec name::: %s" % pname)

        status, output = commands.getstatusoutput(pname)
        logger.debug("Convert output:::\n\t%s"%output)
        if status:
            raise EmacsNotFoundException("orgfile filter failed")
        
        html = temp_file.name[:-4] + '.html'
        temp_file.close()

        #IMO codecs.open is broken on Win32.
        #It refuses to open files without replacing newlines with CR+LF
        #reverting to regular open and decode:
        content = open(html, "rb").read().decode(bf.config.blog_post_encoding)

        # remote the temporary file
        os.remove(html)

        soup = BeautifulSoup(content)

        # the first h2 section will be used for title, category, and date
        metaline = soup.find('div', {'id': 'outline-container-1'}).h2

        # extract title
        try:
            self.title = re.sub('&nbsp;', '', metaline.contents[0]).strip()
        except AttributeError:
            self.title = None

        # extract category
        try:
            categories = metaline('span', {'class':'tag'})[0].string
            self.categories = set([post.Category(x)
                    for x in categories.split('&nbsp;')])
        except:
            self.categories = None

        # extract date
        try:
            date = metaline('span', {'class':'timestamp'})[0].string # 2009-08-22 Sat 15:22
            # date_format = "%Y/%m/%d %H:%M:%S"
            self.date = datetime.datetime.strptime(date, "%Y-%m-%d %a %H:%M")
            self.date = self.date.replace(
                    tzinfo=pytz.timezone(bf.config.blog_timezone))
        except:
            self.date = None

        # delete first h2 section (which is title and category)
        try:
            metaline.extract()
        except AttributeError:
            pass

        # print soup.body
        try:
            toc = soup.find('div',{'id': 'table-of-contents'})
            content = soup.find('div', {'id': 'outline-container-1'})

            if toc != None:
                content = str(toc) + str(content)
                
            self.content = str(content).decode(bf.config.blog_post_encoding)
        except:
            pass


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)

