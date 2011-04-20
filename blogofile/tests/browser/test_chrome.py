# -*- coding: utf-8 -*-
# Selenium tests for the builtin Blogofile server. This is only
# intended to be run in a virtualenv via tox. Selenium isn't working
# for me in Python3 right now. Blogofile will be run using the
# virtualenv python but selenium will be run with the system python2.

import unittest
import tempfile
import shutil
import os
import subprocess
import shlex
import time
import datetime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

def browserbot(driver, function, *args):
    """Selenium Javascript Helpers"""
    # Original copyright and license for browserbot.js (http://is.gd/Bz4xPc):
    # Copyright (c) 2009-2011 Jari Bakken

    # Permission is hereby granted, free of charge, to any person obtaining
    # a copy of this software and associated documentation files (the
    # "Software", to) deal in the Software without restriction, including
    # without limitation the rights to use, copy, modify, merge, publish,
    # distribute, sublicense, and/or sell copies of the Software, and to
    # permit persons to whom the Software is furnished to do so, subject to
    # the following conditions:

    # The above copyright notice and this permission notice shall be
    # included in all copies or substantial portions of the Software.

    # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    # EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    # MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    # NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
    # LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
    # OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
    # WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
    browserbot_js = """var browserbot = {

        getOuterHTML: function(element) {
            if (element.outerHTML) {
                return element.outerHTML;
            } else if (typeof(XMLSerializer) != undefined) {
                return new XMLSerializer().serializeToString(element);
            } else {
                throw "can't get outerHTML in this browser";
            }
        }

    };
    """
    js = browserbot_js + \
        "return browserbot.{0}.apply(browserbot, arguments);".format(function)
    return driver.execute_script(js,*args)

def html(web_element):
    """Return the HTML for a Selenium WebElement"""
    return browserbot(web_element.parent, "getOuterHTML", web_element)

class TestBrowser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        #Remember the current directory to preserve state
        cls.previous_cwd = os.getcwd()
        #Create a staging directory that we can build in
        cls.build_path = tempfile.mkdtemp()
        #Change to that directory just like a user would
        os.chdir(cls.build_path)
        #Initialize and build the site
        subprocess.Popen(shlex.split("blogofile init blog_unit_test"),
                         stdout=subprocess.PIPE).wait()
        subprocess.Popen(shlex.split("blogofile build"),
                         stdout=subprocess.PIPE).wait()
        #Start the server
        cls.port = 42042
        cls.url = u"http://localhost:{0}".format(cls.port)
        cls.server = subprocess.Popen(shlex.split("blogofile serve {0}".
                                                   format(cls.port)),
                                      stdout=subprocess.PIPE)
        cls.chrome = webdriver.Chrome()
    @classmethod
    def tearDownClass(cls):
        cls.chrome.stop_client()
        #Stop the server
        cls.server.kill()
        #go back to the directory we used to be in
        os.chdir(cls.previous_cwd)
        #Clean up the build directory
        shutil.rmtree(cls.build_path)
        
    def testMainPage(self):
        self.chrome.get(self.url)
        self.assertEqual(self.chrome.current_url,self.url+u"/")
        self.assertEqual(self.chrome.title,u"Your Blog's Name")

    def testChronlogicalBlog(self):
        self.chrome.get(self.url)
        #Click on "chronological blog page" link on index
        self.chrome.find_element_by_link_text("chronological blog page").click()
        #Make sure we went to the right URL:
        self.assertEqual(self.chrome.current_url,self.url+u"/blog/")
        #Make sure there are five blog posts:
        self.assertEqual(len(self.chrome.find_elements_by_class_name("blog_post")),5)
        #Make sure there is no previous page:
        with self.assertRaises(NoSuchElementException):
            self.chrome.find_element_by_partial_link_text("Previous Page")
        #Go to the next page:
        self.chrome.find_element_by_partial_link_text("Next Page").click()
        #Make sure we went to the right URL:
        self.assertEqual(self.chrome.current_url,self.url+u"/blog/page/2/")
        #Make sure there are five blog posts:
        self.assertEqual(len(self.chrome.find_elements_by_class_name("blog_post")),5)
        #Go to the last page:
        self.chrome.find_element_by_partial_link_text("Next Page").click()
        #Make sure there is no next page:
        with self.assertRaises(NoSuchElementException):
            self.chrome.find_element_by_partial_link_text("Next Page")
        #Go back to the start:
        self.chrome.find_element_by_partial_link_text("Previous Page").click()
        self.chrome.find_element_by_partial_link_text("Previous Page").click()
        self.assertEqual(self.chrome.current_url,self.url+u"/blog/page/1/")
        #Make sure the unpublished draft is not present. It would be
        #the very first post on the first page if it were actually
        #published:
        with self.assertRaises(NoSuchElementException):
            self.chrome.find_element_by_link_text("This post is unpublished")

    def testPostFeatures(self):
        self.chrome.get(self.url+"/blog")
        self.chrome.find_element_by_link_text("Post 7").click()
        self.assertEqual(self.chrome.current_url,self.url+u"/blog/2009/08/29/post-seven/")
        self.assertEqual(self.chrome.find_element_by_class_name("post_prose").text,u"This is post #7")
        self.assertEqual(self.chrome.find_element_by_class_name("blog_post_date").text,u"August 29, 2009 at 03:25 PM")
        self.assertEqual(self.chrome.find_element_by_class_name("blog_post_categories").text,u"general stuff")
        self.chrome.find_element_by_link_text("general stuff").click()
        self.assertEqual(self.chrome.current_url,self.url+u"/blog/category/general-stuff/")
        
    def testPostWithNoDate(self):
        self.chrome.get(self.url+"/blog")
        self.chrome.find_element_by_link_text("Post without a date").click()
        #Make sure the post has today's date
        now = datetime.datetime.now().strftime("%B %d, %Y")
        #I guess this might fail at 23:59:59..
        self.assertTrue(self.chrome.find_element_by_class_name("blog_post_date").text.startswith(now))

    def testPostUnicode(self):
        self.chrome.get(self.url+"/blog/2009/08/22/unicode-test-")
        self.assertIn("私はガラスを食べられます。それは私を傷つけません".decode("utf-8"), self.chrome.get_page_source())
        self.assertIn("日本語テスト".decode("utf-8"), self.chrome.find_element_by_css_selector(".blog_post_title a").text)

    def testMarkdownTemplate(self):
        self.chrome.get(self.url+"/markdown_test.html")
        self.assertIn("<a href=\"http://www.blogofile.com\">This is a link</a>", self.chrome.get_page_source())
